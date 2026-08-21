from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ArtworkOut(BaseModel):
    id: UUID
    episode_id: UUID
    artwork_type: str
    storage_key: str
    original_filename: str
    width: int
    height: int
    file_size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True
