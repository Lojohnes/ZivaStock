from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.import_batch import ImportBatchResponse, FieldMappingRequest
from app.services.import_service import ImportService
from app.api.deps import get_current_user_id
from app.core.config import settings
import os

router = APIRouter()

UPLOAD_DIR = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=ImportBatchResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    source: str = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Upload file for import and detect row count"""
    import pandas as pd
    from io import BytesIO

    file_content = await file.read()

    # Detect row count from file content
    df = None
    try:
        fname = (file.filename or "").lower()
        if fname.endswith(".xlsx") or fname.endswith(".xls"):
            df = pd.read_excel(BytesIO(file_content))
            # If all columns unnamed, scan for real header row
            if all(str(c).startswith('Unnamed') for c in df.columns):
                raw = pd.read_excel(BytesIO(file_content), header=None)
                for i, row in raw.iterrows():
                    vals = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
                    if len(vals) >= 3:
                        df = pd.read_excel(BytesIO(file_content), header=i)
                        break
        else:
            df = pd.read_csv(BytesIO(file_content))
        total_records = len(df)
    except Exception:
        total_records = 0

    # Save file to disk keyed by a temp name
    safe_name = f"{user_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(file_content)

    # Detect column names
    try:
        detected_columns = list(df.columns.astype(str)) if df is not None else []
    except Exception:
        detected_columns = []

    import_service = ImportService(db)
    import_batch = import_service.create_import_batch(
        filename=file.filename,
        source=source,
        uploaded_by=user_id,
        total_records=total_records
    )

    # Store the saved path on the batch so process can find it
    import_batch.file_path = save_path
    db.commit()
    db.refresh(import_batch)

    response = import_batch.__dict__.copy()
    response['detected_columns'] = detected_columns
    return response


@router.post("/process/{batch_id}")
async def process_import(
    batch_id: int,
    field_mapping: FieldMappingRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Process import with field mapping — reads the saved file and upserts products"""
    import_service = ImportService(db)

    batch = import_service.get_import_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found")

    file_path = getattr(batch, "file_path", None)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file not found on server. Please upload again."
        )

    with open(file_path, "rb") as f:
        file_content = f.read()

    fname = (batch.filename or "").lower()
    mapping = field_mapping.field_mapping

    try:
        if fname.endswith(".xlsx") or fname.endswith(".xls"):
            result = import_service.process_excel_import(file_content, mapping, batch_id)
        else:
            result = import_service.process_csv_import(file_content, mapping, batch_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Clean up file after processing
    try:
        os.remove(file_path)
    except Exception:
        pass

    return result
