from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import String, or_
from typing import List, Optional
import uuid

from app.database import get_db
from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.schemas.show import ShowCreate, ShowUpdate, ShowOut
from app.dependencies import get_editor_user
from app.models.user import User

router = APIRouter(prefix="/admin/shows", tags=["shows"])

@router.get("", response_model=List[ShowOut])
async def list_shows(
    q: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    offset: int = 0,
    limit: int = 25,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    query = select(Show)

    if language:
        query = (
            query
            .join(Season, Season.show_id == Show.id)
            .join(Episode, Episode.season_id == Season.id)
            .where(Episode.language == language)
            .distinct()
        )

    if q:
        term = f"%{q}%"
        query = query.where(or_(
            Show.title.ilike(term),
            Show.slug.ilike(term),
            Show.synopsis.ilike(term),
            Show.categories.cast(String).ilike(term),
        ))
    if section:
        query = query.where(Show.section == section)
    if status:
        query = query.where(Show.status == status)

    safe_limit = min(max(limit, 1), 100)
    safe_offset = max(offset, 0)
    result = await db.execute(query.order_by(Show.title).offset(safe_offset).limit(safe_limit))
    return result.scalars().all()

@router.get("/{show_id}", response_model=ShowOut)
async def get_show(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    show = await db.get(Show, show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return show

@router.post("", response_model=ShowOut)
async def create_show(
    show_in: ShowCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    # Check slug uniqueness
    result = await db.execute(select(Show).where(Show.slug == show_in.slug))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Slug already exists")
        
    show = Show(**show_in.model_dump())
    db.add(show)
    await db.commit()
    await db.refresh(show)
    return show

@router.put("/{show_id}", response_model=ShowOut)
async def update_show(
    show_id: uuid.UUID,
    show_in: ShowUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    show = await db.get(Show, show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    if show_in.slug != show.slug:
        result = await db.execute(select(Show).where(Show.slug == show_in.slug))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Slug already exists")
            
    for key, value in show_in.model_dump().items():
        setattr(show, key, value)
        
    await db.commit()
    await db.refresh(show)
    return show

@router.delete("/{show_id}", status_code=204)
async def delete_show(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    show = await db.get(Show, show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    await db.delete(show)
    await db.commit()
