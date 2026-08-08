from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ImportBatchResponse(BaseModel):
    id: int
    filename: str
    entity_type: str
    status: str
    total_records: int
    success_count: int
    error_count: int
    uploaded_by: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    detected_columns: Optional[list] = None

    class Config:
        from_attributes = True


class FieldMappingRequest(BaseModel):
    field_mapping: dict


class ImportProcessRequest(BaseModel):
    pass
