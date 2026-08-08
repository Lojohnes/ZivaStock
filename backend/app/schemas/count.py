from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CountBase(BaseModel):
    session_id: int
    product_id: int
    shelf_section_id: int
    quantity: Decimal = Field(..., ge=0)
    client_id: Optional[str] = None
    device_id: Optional[str] = None
    source: str = Field("mobile", pattern="^(mobile|web|api|import)$")


class FirstCountCreate(CountBase):
    pass


class SecondCountCreate(CountBase):
    first_count_id: Optional[int] = None


class CountUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None, ge=0)


class FirstCountResponse(BaseModel):
    id: int
    session_id: int
    product_id: int
    shelf_section_id: int
    user_id: int
    quantity: Decimal
    client_id: Optional[str]
    device_id: Optional[str]
    source: str
    counted_at: datetime
    is_synced: bool
    synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class SecondCountResponse(BaseModel):
    id: int
    session_id: int
    product_id: int
    shelf_section_id: int
    user_id: int
    first_count_id: Optional[int]
    quantity: Decimal
    client_id: Optional[str]
    device_id: Optional[str]
    source: str
    counted_at: datetime
    is_synced: bool
    synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class FirstCountWithDetails(FirstCountResponse):
    product: Optional["ProductResponse"] = None
    shelf_section: Optional["ShelfSectionResponse"] = None
    user: Optional["UserResponse"] = None


class SecondCountWithDetails(SecondCountResponse):
    product: Optional["ProductResponse"] = None
    shelf_section: Optional["ShelfSectionResponse"] = None
    user: Optional["UserResponse"] = None


class DiscrepancyResponse(BaseModel):
    product_id: int
    shelf_section_id: int
    first_quantity: Decimal
    second_quantity: Decimal
    difference: Decimal
    difference_pct: Optional[Decimal]


# Forward references
from app.schemas.product import ProductResponse
from app.schemas.location import ShelfSectionResponse
from app.schemas.user import UserResponse
FirstCountWithDetails.model_rebuild()
SecondCountWithDetails.model_rebuild()
