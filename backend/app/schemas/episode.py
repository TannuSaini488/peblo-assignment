from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.artwork import ArtworkOut

class EpisodeBase(BaseModel):
    episode_number: int
    episode_title: str
    duration_seconds: Optional[int] = None
    language: str
    content_group: str
    status: str

class EpisodeCreate(EpisodeBase):
    pass

class EpisodeUpdate(EpisodeBase):
    pass

class EpisodeOut(EpisodeBase):
    id: UUID
    season_id: UUID
    created_at: datetime
    updated_at: datetime
    artwork: List[ArtworkOut] = []

    class Config:
        from_attributes = True
