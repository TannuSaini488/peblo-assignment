from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List
import uuid
import os

from app.database import get_db
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.schemas.artwork import ArtworkOut
from app.dependencies import get_editor_user, get_storage
from app.storage.base import StorageBackend
from app.models.user import User
from app.services.artwork_service import validate_artwork

router = APIRouter(tags=["artwork"])

@router.get("/admin/episodes/{episode_id}/artwork", response_model=List[ArtworkOut])
async def list_artwork(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_editor_user)
):
    result = await db.execute(select(Artwork).where(Artwork.episode_id == episode_id))
    return result.scalars().all()

@router.post("/admin/episodes/{episode_id}/artwork/{artwork_type}", response_model=ArtworkOut)
async def upload_artwork(
    episode_id: uuid.UUID,
    artwork_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
    user: User = Depends(get_editor_user)
):
    episode = await db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
        
    file_data = await file.read()
    
    # 1. Validate artwork
    dimensions = validate_artwork(artwork_type, file_data)
    
    # 2. Upload to storage
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    storage_key = f"artwork/{episode_id}/{artwork_type}{file_ext}"
    await storage.put(storage_key, file_data, file.content_type or "image/jpeg")
    
    # 3. Save to database
    # Check if exists first to update, or use upsert logic. We'll do simple check.
    result = await db.execute(
        select(Artwork).where(
            Artwork.episode_id == episode_id, 
            Artwork.artwork_type == artwork_type
        )
    )
    existing_artwork = result.scalars().first()
    
    if existing_artwork:
        existing_artwork.storage_key = storage_key
        existing_artwork.original_filename = file.filename
        existing_artwork.width = dimensions["width"]
        existing_artwork.height = dimensions["height"]
        existing_artwork.file_size_bytes = dimensions["size_bytes"]
        artwork = existing_artwork
    else:
        artwork = Artwork(
            episode_id=episode_id,
            artwork_type=artwork_type,
            storage_key=storage_key,
            original_filename=file.filename,
            width=dimensions["width"],
            height=dimensions["height"],
            file_size_bytes=dimensions["size_bytes"]
        )
        db.add(artwork)
        
    await db.commit()
    await db.refresh(artwork)
    
    return artwork

@router.delete("/admin/artwork/{artwork_id}", status_code=204)
async def delete_artwork(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
    user: User = Depends(get_editor_user)
):
    artwork = await db.get(Artwork, artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
        
    await storage.delete(artwork.storage_key)
    
    await db.delete(artwork)
    await db.commit()
