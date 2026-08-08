from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    parent = relationship("ProductCategory", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=True)
    barcode = Column(String(50), unique=True, nullable=False, index=True)
    product_code = Column(String(50), nullable=True, index=True)
    category_id = Column(BigInteger, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(String(500), nullable=False)
    unit_of_measure = Column(String(20), default="EA")
    system_quantity = Column(Numeric(18, 4), default=0)
    unit_cost = Column(Numeric(18, 4), default=0)
    unit_price = Column(Numeric(18, 4), default=0)
    reorder_level = Column(Numeric(18, 4), default=0)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    first_counts = relationship("FirstCount", back_populates="product")
    second_counts = relationship("SecondCount", back_populates="product")
