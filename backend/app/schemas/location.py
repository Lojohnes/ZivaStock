from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(store|warehouse|zone|area)$")
    parent_id: Optional[int] = None
    address: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(store|warehouse|zone|area)$")
    parent_id: Optional[int] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class LocationResponse(BaseModel):
    id: int
    name: str
    type: str
    parent_id: Optional[int]
    address: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShelfBase(BaseModel):
    location_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ShelfCreate(ShelfBase):
    pass


class ShelfUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ShelfResponse(BaseModel):
    id: int
    location_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShelfSectionBase(BaseModel):
    shelf_id: int
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ShelfSectionCreate(ShelfSectionBase):
    pass


class ShelfSectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ShelfSectionResponse(BaseModel):
    id: int
    shelf_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
