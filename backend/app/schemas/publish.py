from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime

class PublishRunOut(BaseModel):
    id: UUID
    published_by: Optional[UUID] = None
    published_at: datetime
    show_count: int
    episode_count: int
    catalogue_key: Optional[str] = None
    outcome: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class ValidationError(BaseModel):
    show_id: Union[UUID, str]
    show_title: str
    season_id: Optional[UUID] = None
    season_number: Optional[int] = None
    episode_id: Optional[UUID] = None
    episode_title: Optional[str] = None
    error_type: str
    message: str

class ValidationReport(BaseModel):
    blocking_errors: List[ValidationError]
    warnings: List[ValidationError]
