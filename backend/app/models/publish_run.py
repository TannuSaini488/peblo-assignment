from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class PublishRun(Base):
    __tablename__ = "publish_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    show_count = Column(Integer, nullable=False)
    episode_count = Column(Integer, nullable=False)
    catalogue_key = Column(String(500), nullable=True)
    outcome = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="publish_runs")
