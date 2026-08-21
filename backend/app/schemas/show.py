from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ShowBase(BaseModel):
    title: str
    slug: str
    section: Optional[str] = None
    categories: List[str]
    synopsis: str
    status: str

class ShowCreate(ShowBase):
    pass

class ShowUpdate(ShowBase):
    pass

class ShowOut(ShowBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
