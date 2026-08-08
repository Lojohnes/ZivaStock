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
    file_content = await file.read()

    import_service = ImportService(db)

    # Read file and auto-detect header row (handles title/blank rows)
    try:
        df = import_service.read_import_file(file_content, file.filename or "")
        total_records = len(df)
        detected_columns = list(df.columns.astype(str))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse the uploaded file. Please ensure it is a valid CSV/Excel file with a header row. Error: {exc}"
        )

    if total_records == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data rows found after the header. Please check the file contents."
        )

    # Save file to disk keyed by a temp name
    safe_name = f"{user_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(file_content)

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
