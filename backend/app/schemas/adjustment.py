from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AdjustmentResponse(BaseModel):
    id: int
    session_id: int
    product_id: int
    shelf_section_id: Optional[int]
    first_count_id: Optional[int]
    second_count_id: Optional[int]
    system_quantity: Decimal
    final_quantity: Decimal
    variance_quantity: Optional[Decimal]
    unit_cost_snapshot: Decimal
    variance_value: Optional[Decimal]
    adjustment_type: str
    reason: Optional[str]
    status: str
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    posted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdjustmentRejectRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=2000)


class SessionVarianceResponse(BaseModel):
    total_products: int
    total_adjustments: int
    total_variance_quantity: Decimal
    total_variance_value: Decimal
    overcount_products: int
    undercount_products: int
    accurate_products: int
