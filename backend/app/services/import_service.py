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
        """Shared logic to upsert products from a DataFrame"""
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

        for index, row in df.iterrows():
            barcode = str(self._get_cell(row, field_mapping, 'barcode', '')).strip()
            # Skip empty, header repeat rows, date strings, and long text (report titles)
            if (not barcode
                    or barcode.lower() in SKIP_BARCODES
                    or barcode.lower().startswith('sage ')
                    or barcode.lower().startswith('inventory ')
                    or barcode.lower().startswith('page ')
                    or '/' in barcode and len(barcode) > 8  # date strings like 5/15/2026 9:44:57 AM
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

                existing = self.db.query(Product).filter(
                    Product.barcode == barcode
                ).first()

                if existing:
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                else:
                    self.db.add(Product(**product_data))

                self.db.commit()
                success_count += 1

            except Exception as e:
                self.db.rollback()
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")

        self.update_import_batch(batch_id, "completed", success_count, error_count)
        return {'success_count': success_count, 'error_count': error_count, 'errors': errors[:50]}

    def process_excel_import(self, file_content: bytes, field_mapping: dict, batch_id: int) -> dict:
        """Process Excel file import — auto-detects header row"""
        try:
            # Try default header first
            df = pd.read_excel(BytesIO(file_content))
            # If columns are all unnamed, scan for the real header row
            if all(str(c).startswith('Unnamed') for c in df.columns):
                raw = pd.read_excel(BytesIO(file_content), header=None)
                header_row = None
                for i, row in raw.iterrows():
                    vals = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
                    if len(vals) >= 3:
                        header_row = i
                        break
                if header_row is not None:
                    df = pd.read_excel(BytesIO(file_content), header=header_row)
            return self._process_dataframe(df, field_mapping, batch_id)
        except Exception as e:
            self.db.rollback()
            self.update_import_batch(batch_id, "failed", 0, 0)
            raise e

    def process_csv_import(self, file_content: bytes, field_mapping: dict, batch_id: int) -> dict:
        """Process CSV file import"""
        try:
            df = pd.read_csv(BytesIO(file_content))
            return self._process_dataframe(df, field_mapping, batch_id)
        except Exception as e:
            self.db.rollback()
            self.update_import_batch(batch_id, "failed", 0, 0)
            raise e
