from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("locations.id"), nullable=True, index=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    parent = relationship("Location", remote_side=[id], backref="children")
    shelves = relationship("Shelf", back_populates="location")
    sessions = relationship("StocktakeSession", back_populates="location")


class Shelf(Base):
    __tablename__ = "shelves"

    id = Column(BigInteger, primary_key=True, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    location = relationship("Location", back_populates="shelves")
    sections = relationship("ShelfSection", back_populates="shelf")


class ShelfSection(Base):
    __tablename__ = "shelf_sections"

    id = Column(BigInteger, primary_key=True, index=True)
    shelf_id = Column(BigInteger, ForeignKey("shelves.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    shelf = relationship("Shelf", back_populates="sections")
    first_counts = relationship("FirstCount", back_populates="shelf_section")
    second_counts = relationship("SecondCount", back_populates="shelf_section")
