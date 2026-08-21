from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    episode_title = Column(String(255), nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    language = Column(String(10), nullable=False)
    content_group = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default='draft')
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    season = relationship("Season", back_populates="episodes")
    artwork = relationship("Artwork", back_populates="episode", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('content_group', 'language', name='uix_content_group_language'),
        Index('idx_content_group', 'content_group'),
        Index('idx_season_id_episode_number', 'season_id', 'episode_number'),
    )
