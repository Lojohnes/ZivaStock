from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib
from app.core.database import Base


class ExportJob(Base):
    __tablename__ = "exports"

    id = Column(BigInteger, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    export_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    filters = Column(JSONB, nullable=False, default=dict)
    file_path = Column(String(512), nullable=True)
    file_format = Column(String(10), default="xlsx", nullable=False)
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(String, nullable=True)
    requested_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    download_count = Column(Integer, default=0, nullable=False)

    requester = relationship("User")
