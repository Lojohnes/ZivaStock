from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SyncQueue(Base):
    __tablename__ = "sync_queue"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(100), nullable=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    client_id = Column(String(100), nullable=False)
    action = Column(String(20), nullable=False)
    payload = Column(JSONB, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('user_id', 'client_id', name='uq_sync_queue_user_client'),
        CheckConstraint("action IN ('create', 'update', 'delete')", name='chk_sync_action'),
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name='chk_sync_status'),
    )
