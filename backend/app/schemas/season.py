from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class SeasonBase(BaseModel):
    season_number: int

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(SeasonBase):
    pass

class SeasonOut(SeasonBase):
    id: UUID
    show_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
