from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductWithCategory,
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.product_service import ProductService
from app.models.user import User
from app.api.deps import get_current_user_id, require_permission

router = APIRouter()


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.create")),
):
    """Create a new product (requires products.create permission)"""
    product_service = ProductService(db)
    try:
        product = product_service.create_product(product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categories", response_model=List[ProductCategoryResponse])
def get_categories(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get all product categories"""
    return ProductService(db).get_categories()


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: ProductCategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.create")),
):
    """Create a product category (requires products.create permission)"""
    return ProductService(db).create_category(data)


@router.put("/categories/{category_id}", response_model=ProductCategoryResponse)
def update_category(
    category_id: int,
    data: ProductCategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.update")),
):
    """Update a product category (requires products.update permission)"""
    category = ProductService(db).update_category(category_id, data)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.delete")),
):
    """Delete a product category (requires products.delete permission)"""
    success = ProductService(db).delete_category(category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"message": "Category deleted successfully"}


@router.get("", response_model=PaginatedResponse[ProductResponse])
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=5000),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    sort: str = Query("description"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get products with pagination"""
    product_service = ProductService(db)
    skip = (page - 1) * limit
    products, total = product_service.get_products(skip=skip, limit=limit, search=search, category_id=category_id, is_active=is_active, sort=sort, order=order)
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        items=products,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get product by barcode"""
    product_service = ProductService(db)
    product = product_service.get_product_by_barcode(barcode)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get product by ID"""
    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.update")),
):
    """Update product (requires products.update permission)"""
    product_service = ProductService(db)
    product = product_service.update_product(product_id, product_data)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("products.delete")),
):
    """Delete product (requires products.delete permission)"""
    product_service = ProductService(db)
    success = product_service.delete_product(product_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return {"message": "Product deleted successfully"}
