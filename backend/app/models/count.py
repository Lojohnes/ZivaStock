from sqlalchemy import Column, BigInteger, Numeric, DateTime, ForeignKey, Boolean, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FirstCount(Base):
    __tablename__ = "first_counts"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    shelf_section_id = Column(BigInteger, ForeignKey("shelf_sections.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    client_id = Column(String(100), nullable=True)
    device_id = Column(String(100), nullable=True)
    source = Column(String(20), default="mobile", nullable=False)
    counted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    is_synced = Column(Boolean, default=False, nullable=False, index=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("StocktakeSession", back_populates="first_counts")
    product = relationship("Product", back_populates="first_counts")
    shelf_section = relationship("ShelfSection", back_populates="first_counts")
    user = relationship("User", back_populates="first_counts", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint('session_id', 'product_id', 'shelf_section_id', 'user_id', name='uq_first_count_scope'),
        UniqueConstraint('user_id', 'client_id', name='uq_first_count_client'),
        CheckConstraint("source IN ('mobile', 'web', 'api', 'import')", name='chk_first_counts_source'),
        CheckConstraint("quantity >= 0", name='chk_first_counts_qty_nonneg'),
    )


class SecondCount(Base):
    __tablename__ = "second_counts"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    shelf_section_id = Column(BigInteger, ForeignKey("shelf_sections.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    first_count_id = Column(BigInteger, ForeignKey("first_counts.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Numeric(18, 4), nullable=False)
    client_id = Column(String(100), nullable=True)
    device_id = Column(String(100), nullable=True)
    source = Column(String(20), default="mobile", nullable=False)
    counted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    is_synced = Column(Boolean, default=False, nullable=False, index=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("StocktakeSession", back_populates="second_counts")
    product = relationship("Product", back_populates="second_counts")
    shelf_section = relationship("ShelfSection", back_populates="second_counts")
    user = relationship("User", back_populates="second_counts", foreign_keys=[user_id])
    first_count = relationship("FirstCount", foreign_keys=[first_count_id])

    __table_args__ = (
        UniqueConstraint('session_id', 'product_id', 'shelf_section_id', 'user_id', name='uq_second_count_scope'),
        UniqueConstraint('user_id', 'client_id', name='uq_second_count_client'),
        CheckConstraint("source IN ('mobile', 'web', 'api', 'import')", name='chk_second_counts_source'),
        CheckConstraint("quantity >= 0", name='chk_second_counts_qty_nonneg'),
    )
