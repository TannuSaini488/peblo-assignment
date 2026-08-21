from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List
import uuid

from app.database import get_db
from app.models.season import Season
from app.models.show import Show
from app.schemas.season import SeasonCreate, SeasonUpdate, SeasonOut
from app.dependencies import get_editor_user
from app.models.user import User

router = APIRouter(tags=["seasons"])

@router.get("/admin/shows/{show_id}/seasons", response_model=List[SeasonOut])
async def list_seasons(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    result = await db.execute(
        select(Season).where(Season.show_id == show_id).order_by(Season.season_number)
    )
    return result.scalars().all()

@router.post("/admin/shows/{show_id}/seasons", response_model=SeasonOut)
async def create_season(
    show_id: uuid.UUID,
    season_in: SeasonCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    show = await db.get(Show, show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    season = Season(show_id=show_id, **season_in.model_dump())
    db.add(season)
    try:
        await db.commit()
        await db.refresh(season)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Season number already exists for this show")
        
    return season

@router.delete("/admin/seasons/{season_id}", status_code=204)
async def delete_season(
    season_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    season = await db.get(Season, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
        
    await db.delete(season)
    await db.commit()
