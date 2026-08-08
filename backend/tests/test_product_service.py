import pytest
from app.services.product_service import ProductService
from app.models.product import Product
from app.schemas.product import ProductCreate
from sqlalchemy.orm import Session


def test_create_product_success(db_session: Session):
    """Test successful product creation"""
    product_service = ProductService(db_session)
    
    product_data = ProductCreate(
        barcode="1234567890123",
        product_code="PROD001",
        description="Test Product",
        unit_of_measure="EA",
        system_quantity=100.0,
        unit_cost=10.50
    )
    
    product = product_service.create_product(product_data)
    
    assert product.barcode == "1234567890123"
    assert product.description == "Test Product"
    assert product.system_quantity == 100.0


def test_get_product_by_barcode(db_session: Session):
    """Test getting product by barcode"""
    product_service = ProductService(db_session)
    
    # Create a test product
    product_data = ProductCreate(
        barcode="9876543210987",
        product_code="PROD002",
        description="Another Test Product",
        unit_of_measure="EA",
        system_quantity=50.0,
        unit_cost=20.00
    )
    
    created_product = product_service.create_product(product_data)
    
    # Get product by barcode
    retrieved_product = product_service.get_product_by_barcode("9876543210987")
    
    assert retrieved_product is not None
    assert retrieved_product.id == created_product.id
    assert retrieved_product.barcode == "9876543210987"


def test_get_products_pagination(db_session: Session):
    """Test product pagination"""
    product_service = ProductService(db_session)
    
    # Create multiple products
    for i in range(10):
        product_data = ProductCreate(
            barcode=f"BARCODE{i:010d}",
            product_code=f"PROD{i:03d}",
            description=f"Product {i}",
            unit_of_measure="EA",
            system_quantity=float(i * 10),
            unit_cost=float(i)
        )
        product_service.create_product(product_data)
    
    # Get products with pagination
    products, total = product_service.get_products(skip=0, limit=5)
    
    assert len(products) == 5
    assert total == 10
