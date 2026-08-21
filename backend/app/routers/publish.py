from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.dependencies import get_admin_user, get_editor_user, get_storage
from app.models.user import User
from app.models.publish_run import PublishRun
from app.storage.base import StorageBackend
from app.schemas.publish import ValidationReport, PublishRunOut
from app.services.validation_service import generate_validation_report
from app.services.publish_service import publish_catalogue

router = APIRouter(prefix="/admin", tags=["publish"])

@router.get("/validation-report", response_model=ValidationReport)
async def get_validation_report(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    return await generate_validation_report(db)

@router.post("/catalog/publish", response_model=PublishRunOut)
async def publish(
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
    user: User = Depends(get_admin_user)
):
    try:
        run = await publish_catalogue(db, storage, user.id)
        return run
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/catalog/publish-runs", response_model=List[PublishRunOut])
async def list_publish_runs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    result = await db.execute(select(PublishRun).order_by(PublishRun.published_at.desc()))
    return result.scalars().all()
