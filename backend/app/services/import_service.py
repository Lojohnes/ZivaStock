from sqlalchemy.orm import Session
from app.models.import_batch import ImportJob
from app.models.product import Product
from typing import Optional, List
from datetime import datetime
import pandas as pd
from io import BytesIO


class ImportService:
    def __init__(self, db: Session):
        self.db = db

    _HEADER_KEYWORDS = {
        'barcode', 'item code', 'sku', 'product code', 'stock code',
        'description', 'item description', 'qty', 'quantity', 'on hand',
        'unit cost', 'cost', 'price', 'uom', 'unit', 'system quantity',
        'system_quantity',
    }

    def _looks_like_no_header(self, df: pd.DataFrame) -> bool:
        """Heuristic: the file likely has junk/title rows above the header."""
        if df.empty:
            return True
        cols = [str(c) for c in df.columns]
        if len(cols) <= 1:
            return True
        if all(c.startswith('Unnamed') for c in cols):
            return True

        unnamed_count = sum(1 for c in cols if c.startswith('Unnamed'))
        if unnamed_count >= len(cols) - 1:
            return True

        # If the first column header looks like a report title rather than a label,
        # treat the first data row as the header instead.
        first_col = cols[0].lower()
        title_keywords = (
            'inventory', 'valuation', 'sage', 'report', 'generated',
            'page', 'stock', 'item list', 'item master', 'product list',
        )
        if any(kw in first_col for kw in title_keywords):
            return True

        return False

    def _row_looks_like_header(self, vals: list[str]) -> bool:
        lowered = [v.lower() for v in vals]
        # If any known product column keyword is present, treat it as a header.
        has_header_keyword = any(
            kw in v for v in lowered for kw in self._HEADER_KEYWORDS
        )
        return has_header_keyword or len(vals) >= 3

    def _find_header_row(self, raw: pd.DataFrame, max_rows: int = 50) -> int:
        """Scan raw rows and return the first row that looks like a header."""
        for i in range(min(max_rows, len(raw))):
            row = raw.iloc[i]
            vals = [
                str(v).strip()
                for v in row
                if pd.notna(v) and str(v).strip()
            ]
            if len(vals) >= 2 and self._row_looks_like_header(vals):
                return i
        return 0

    def _try_read_csv(self, file_content: bytes, header=None, encoding=None) -> pd.DataFrame:
        from io import BytesIO
        kwargs = {"sep": None, "engine": "python"}  # auto-detect delimiter
        if header is not None:
            kwargs["header"] = header
        if encoding is not None:
            kwargs["encoding"] = encoding
        try:
            return pd.read_csv(BytesIO(file_content), **kwargs)
        except Exception:
            # Fallback to standard comma parsing if auto-detection fails.
            kwargs.pop("sep", None)
            kwargs.pop("engine", None)
            return pd.read_csv(BytesIO(file_content), **kwargs)

    def read_import_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Read a CSV/Excel import file and return a DataFrame with the real
        header row promoted to columns. Leading title/blank rows are skipped."""
        fname = (filename or "").lower()
        from io import BytesIO

        if fname.endswith(".xlsx") or fname.endswith(".xls"):
            df = pd.read_excel(BytesIO(file_content))
            if self._looks_like_no_header(df):
                raw = pd.read_excel(BytesIO(file_content), header=None)
                header_idx = self._find_header_row(raw)
                df = pd.read_excel(BytesIO(file_content), header=header_idx)
        else:
            # Try UTF-8 first, then fall back to Latin-1 for older Windows/Sage exports.
            try:
                df = self._try_read_csv(file_content)
            except UnicodeDecodeError:
                df = self._try_read_csv(file_content, encoding="latin-1")

            if self._looks_like_no_header(df):
                try:
                    raw = self._try_read_csv(file_content, header=None)
                except UnicodeDecodeError:
                    raw = self._try_read_csv(file_content, header=None, encoding="latin-1")
                header_idx = self._find_header_row(raw)
                try:
                    df = self._try_read_csv(file_content, header=header_idx)
                except UnicodeDecodeError:
                    df = self._try_read_csv(file_content, header=header_idx, encoding="latin-1")

        # Drop fully blank rows and normalize column names
        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def create_import_batch(
        self,
        filename: str,
        source: str,
        uploaded_by: int,
        total_records: int
    ) -> ImportJob:
        """Create a new import job.

        The public `source` parameter describes the file origin (e.g. csv,
        excel, sage_evolution), while the `entity_type` column records the
        kind of records being imported and must satisfy the database check
        constraint.
        """
        # Map file-format sources to the entity type they contain.
        # Inventory imports are product imports.
        entity_type = source or "products"
        if entity_type in ("csv", "excel", "xlsx", "xls", "sage_evolution", "manual"):
            entity_type = "products"

        import_batch = ImportJob(
            filename=filename,
            original_filename=filename,
            entity_type=entity_type,
            status="pending",
            total_records=total_records,
            success_count=0,
            error_count=0,
            uploaded_by=uploaded_by
        )
        
        self.db.add(import_batch)
        self.db.commit()
        self.db.refresh(import_batch)
        return import_batch
    
    def get_import_batch(self, batch_id: int) -> Optional[ImportJob]:
        """Get import job by ID"""
        return self.db.query(ImportJob).filter(ImportJob.id == batch_id).first()
    
    def update_import_batch(
        self,
        batch_id: int,
        status: str,
        success_count: int,
        error_count: int
    ) -> Optional[ImportJob]:
        """Update import batch status"""
        batch = self.get_import_batch(batch_id)
        if not batch:
            return None
        
        batch.status = status
        batch.success_count = success_count
        batch.error_count = error_count
        batch.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(batch)
        return batch
    
    def _get_cell(self, row, mapping: dict, field: str, default=''):
        """Safely get a cell value using field mapping"""
        col = mapping.get(field, field)
        val = row.get(col, default)
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return val

    def _process_dataframe(self, df: 'pd.DataFrame', field_mapping: dict, batch_id: int) -> dict:
        """Shared logic to upsert products from a DataFrame in batches"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"DataFrame columns: {list(df.columns)}")
        logger.info(f"Field mapping received: {field_mapping}")
        logger.info(f"Total rows: {len(df)}")
        if len(df) > 0:
            logger.info(f"First row sample: {dict(df.iloc[0])}")

        success_count = 0
        error_count = 0
        errors = []

        SKIP_BARCODES = {'nan', 'none', 'totals', 'item code', 'inventory valuation',
                         'item description', 'value', 'group', 'whse', 'unit cost',
                         'qty on hand', 'sage', 'page', 'description'}

        # Build a deduplicated list of valid product rows keyed by barcode.
        candidate_rows = []
        for index, row in df.iterrows():
            barcode = str(self._get_cell(row, field_mapping, 'barcode', '')).strip()
            # Skip empty, header repeat rows, date strings, and long text (report titles)
            if (not barcode
                    or barcode.lower() in SKIP_BARCODES
                    or barcode.lower().startswith('sage ')
                    or barcode.lower().startswith('inventory ')
                    or barcode.lower().startswith('page ')
                    or ('/' in barcode and len(barcode) > 8)  # date strings like 5/15/2026 9:44:57 AM
                    or len(barcode) > 50):
                continue

            try:
                product_data = {
                    'barcode': barcode,
                    'product_code': str(self._get_cell(row, field_mapping, 'product_code', '')).strip() or None,
                    'description': str(self._get_cell(row, field_mapping, 'description', '')).strip(),
                    'unit_of_measure': str(self._get_cell(row, field_mapping, 'unit_of_measure', 'EA')).strip() or 'EA',
                    'system_quantity': float(self._get_cell(row, field_mapping, 'system_quantity', 0) or 0),
                    'unit_cost': float(self._get_cell(row, field_mapping, 'unit_cost', 0) or 0),
                }
                candidate_rows.append((index + 2, product_data))
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")

        # For large files, process in chunks to avoid per-row commits/timeouts.
        CHUNK_SIZE = 500
        for chunk_start in range(0, len(candidate_rows), CHUNK_SIZE):
            chunk = candidate_rows[chunk_start:chunk_start + CHUNK_SIZE]
            chunk_barcodes = [data['barcode'] for _, data in chunk]
            existing_map = {
                p.barcode: p
                for p in self.db.query(Product).filter(Product.barcode.in_(chunk_barcodes)).all()
            }

            processed_in_chunk = 0
            for row_num, data in chunk:
                try:
                    existing = existing_map.get(data['barcode'])
                    if existing:
                        for key, value in data.items():
                            setattr(existing, key, value)
                    else:
                        self.db.add(Product(**data))
                        # Avoid adding a duplicate barcode again in the same flush.
                        existing_map[data['barcode']] = None
                    processed_in_chunk += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")

            try:
                self.db.commit()
                success_count += processed_in_chunk
            except Exception as e:
                self.db.rollback()
                # If the whole chunk fails, count it as errors.
                failed = processed_in_chunk
                success_count -= (processed_in_chunk - failed) if failed else 0
                error_count += failed
                errors.append(f"Chunk {chunk_start // CHUNK_SIZE + 1}: {str(e)}")

        self.update_import_batch(batch_id, "completed", success_count, error_count)
        return {'success_count': success_count, 'error_count': error_count, 'errors': errors[:50]}

    def process_excel_import(self, file_content: bytes, field_mapping: dict, batch_id: int) -> dict:
        """Process Excel file import — auto-detects header row"""
        try:
            df = self.read_import_file(file_content, "import.xlsx")
            return self._process_dataframe(df, field_mapping, batch_id)
        except Exception as e:
            self.db.rollback()
            self.update_import_batch(batch_id, "failed", 0, 0)
            raise e

    def process_csv_import(self, file_content: bytes, field_mapping: dict, batch_id: int) -> dict:
        """Process CSV file import"""
        try:
            df = self.read_import_file(file_content, "import.csv")
            return self._process_dataframe(df, field_mapping, batch_id)
        except Exception as e:
            self.db.rollback()
            self.update_import_batch(batch_id, "failed", 0, 0)
            raise e
