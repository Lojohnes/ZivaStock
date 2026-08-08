from sqlalchemy import Column, BigInteger, Numeric, DateTime, ForeignKey, String, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Adjustment(Base):
    __tablename__ = "adjustments"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    shelf_section_id = Column(BigInteger, ForeignKey("shelf_sections.id", ondelete="SET NULL"), nullable=True)
    first_count_id = Column(BigInteger, ForeignKey("first_counts.id", ondelete="SET NULL"), nullable=True)
    second_count_id = Column(BigInteger, ForeignKey("second_counts.id", ondelete="SET NULL"), nullable=True)
    system_quantity = Column(Numeric(18, 4), nullable=False)
    final_quantity = Column(Numeric(18, 4), nullable=False)
    variance_quantity = Column(Numeric(18, 4))  # generated column, read-only
    unit_cost_snapshot = Column(Numeric(18, 4), default=0, nullable=False)
    variance_value = Column(Numeric(18, 4))  # generated column, read-only
    adjustment_type = Column(String(20), default="none", nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    approved_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    session = relationship("StocktakeSession", back_populates="adjustments")
    product = relationship("Product")
    shelf_section = relationship("ShelfSection")
    first_count = relationship("FirstCount")
    second_count = relationship("SecondCount")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        UniqueConstraint('session_id', 'product_id', 'shelf_section_id', name='uq_adjustment_scope'),
        CheckConstraint("adjustment_type IN ('increase', 'decrease', 'none')", name='chk_adjustments_type'),
        CheckConstraint("status IN ('pending', 'approved', 'rejected', 'posted')", name='chk_adjustments_status'),
    )
