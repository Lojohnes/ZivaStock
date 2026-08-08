from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    report_type = Column(String(50), nullable=False, index=True)
    session_id = Column(BigInteger, ForeignKey("stocktake_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    generated_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    parameters = Column(JSONB, nullable=False, default=dict)
    file_path = Column(String(512), nullable=True)
    file_format = Column(String(10), default="pdf", nullable=False)
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("StocktakeSession")
    generator = relationship("User")
