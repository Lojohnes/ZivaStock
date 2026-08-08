from sqlalchemy.orm import Session
from app.models.product import Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductCategoryCreate, ProductCategoryUpdate
from typing import Optional, List
from sqlalchemy import or_


class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode"""
        return self.db.query(Product).filter(Product.barcode == barcode).first()
    
    def get_products(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        sort: str = "description",
        order: str = "asc"
    ) -> tuple[List[Product], int]:
        """Get products with pagination and filters"""
        query = self.db.query(Product)

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Product.barcode.ilike(search_pattern),
                    Product.product_code.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )
        
        # Apply sorting
        sort_column = getattr(Product, sort, Product.description)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Check if barcode already exists
        existing = self.get_product_by_barcode(product_data.barcode)
        if existing:
            raise ValueError("Product with this barcode already exists")
        
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = self.get_product(product_id)
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        product = self.get_product(product_id)
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True
    
    def bulk_create_products(self, products_data: List[ProductCreate]) -> List[Product]:
        """Bulk create products"""
        db_products = []
        for product_data in products_data:
            try:
                db_product = self.create_product(product_data)
                db_products.append(db_product)
            except ValueError:
                # Skip duplicates
                continue
        return db_products

    # -------------------------------------------------------------------
    # Product Categories
    # -------------------------------------------------------------------

    def get_categories(self) -> List[ProductCategory]:
        return self.db.query(ProductCategory).order_by(ProductCategory.name).all()

    def get_category(self, category_id: int) -> Optional[ProductCategory]:
        return self.db.query(ProductCategory).filter(ProductCategory.id == category_id).first()

    def create_category(self, data: ProductCategoryCreate) -> ProductCategory:
        category = ProductCategory(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category_id: int, data: ProductCategoryUpdate) -> Optional[ProductCategory]:
        category = self.get_category(category_id)
        if not category:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        category = self.get_category(category_id)
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True
