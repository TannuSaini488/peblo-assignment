from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class CatalogueArtwork(BaseModel):
    poster: Optional[str] = None
    banner: Optional[str] = None
    thumbnail: Optional[str] = None

class CatalogueEpisode(BaseModel):
    episode_number: int
    title: str
    content_group: str
    duration_seconds: int
    languages: List[str]
    artwork: CatalogueArtwork

class CatalogueSeason(BaseModel):
    season_number: int
    episodes: List[CatalogueEpisode]

class CatalogueTrailer(BaseModel):
    title: str
    duration_seconds: int
    languages: List[str]
    artwork: CatalogueArtwork

class CatalogueShow(BaseModel):
    id: str
    title: str
    slug: str
    synopsis: str
    categories: List[str]
    artwork: CatalogueArtwork
    seasons: List[CatalogueSeason]
    trailers: List[CatalogueTrailer]

class CatalogueSection(BaseModel):
    name: str
    shows: List[CatalogueShow]

class Catalogue(BaseModel):
    published_at: str
    sections: List[CatalogueSection]
