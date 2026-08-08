from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditTrail(Base):
    """Maps to the range-partitioned audit_trail table (partitioned by created_at,
    monthly — see database/migrations/V005 and V012). The composite primary key
    is (id, created_at) at the DB level; SQLAlchemy only needs `id` for ORM identity
    since audit rows are never updated/fetched by PK alone in application code."""
    __tablename__ = "audit_trail"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(20), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(BigInteger, nullable=True, index=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, primary_key=True)

    # Relationships
    user = relationship("User", back_populates="audit_entries")
