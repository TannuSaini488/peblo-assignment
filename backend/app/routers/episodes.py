from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List
import uuid

from app.database import get_db
from app.models.episode import Episode
from app.models.season import Season
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeOut
from app.dependencies import get_editor_user
from app.models.user import User

router = APIRouter(tags=["episodes"])

@router.get("/admin/seasons/{season_id}/episodes", response_model=List[EpisodeOut])
async def list_episodes(
    season_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    result = await db.execute(
        select(Episode)
        .options(selectinload(Episode.artwork))
        .where(Episode.season_id == season_id)
        .order_by(Episode.episode_number)
    )
    return result.scalars().all()

@router.post("/admin/seasons/{season_id}/episodes", response_model=EpisodeOut)
async def create_episode(
    season_id: uuid.UUID,
    episode_in: EpisodeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    season = await db.get(Season, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
        
    episode = Episode(season_id=season_id, **episode_in.model_dump())
    db.add(episode)
    try:
        await db.commit()
        await db.refresh(episode)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Content group and language combination must be unique")
        
    # Re-fetch to load artwork relationship (empty)
    result = await db.execute(select(Episode).options(selectinload(Episode.artwork)).where(Episode.id == episode.id))
    return result.scalars().first()

@router.put("/admin/episodes/{episode_id}", response_model=EpisodeOut)
async def update_episode(
    episode_id: uuid.UUID,
    episode_in: EpisodeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    episode = await db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
            
    for key, value in episode_in.model_dump().items():
        setattr(episode, key, value)
        
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Content group and language combination must be unique")
        
    result = await db.execute(select(Episode).options(selectinload(Episode.artwork)).where(Episode.id == episode.id))
    return result.scalars().first()

@router.delete("/admin/episodes/{episode_id}", status_code=204)
async def delete_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    episode = await db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
        
    await db.delete(episode)
    await db.commit()
