from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    parent_id: Optional[int] = None
    description: Optional[str] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: Optional[str] = Field(None, max_length=50)
    barcode: str = Field(..., min_length=1, max_length=50)
    product_code: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = None
    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measure: str = "EA"
    system_quantity: Decimal = Field(default=0, ge=0)
    unit_cost: Decimal = Field(default=0, ge=0)
    unit_price: Decimal = Field(default=0, ge=0)
    reorder_level: Decimal = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=50)
    product_code: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    unit_of_measure: Optional[str] = None
    system_quantity: Optional[Decimal] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    sku: Optional[str]
    barcode: str
    product_code: Optional[str]
    category_id: Optional[int]
    description: str
    unit_of_measure: str
    system_quantity: Decimal
    unit_cost: Decimal
    unit_price: Decimal
    reorder_level: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithCategory(ProductResponse):
    category: Optional[ProductCategoryResponse] = None
