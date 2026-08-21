from sqlalchemy import Column, String, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class SeedAnomaly(Base):
    __tablename__ = "seed_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_type = Column(String(50), nullable=False)
    item_id = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
