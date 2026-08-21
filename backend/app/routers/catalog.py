from fastapi import APIRouter, Depends, HTTPException, Query
import json
from typing import Optional, List

from app.dependencies import get_storage
from app.storage.base import StorageBackend

router = APIRouter(prefix="/catalog", tags=["catalog"])

async def get_catalogue_data(storage: StorageBackend) -> dict:
    try:
        data = await storage.get("catalogue.json")
        return json.loads(data)
    except Exception:
        raise HTTPException(status_code=404, detail="Catalogue not found. Please publish first.")

@router.get("")
async def get_catalog(storage: StorageBackend = Depends(get_storage)):
    """
    Returns the currently published catalogue.
    """
    return await get_catalogue_data(storage)

@router.get("/search")
async def search_catalog(
    q: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    section: Optional[str] = None,
    storage: StorageBackend = Depends(get_storage)
):
    """
    Search the published catalogue.
    Filters:
    - q: show title, episode title, category
    - category
    - language
    - section
    """
    catalogue = await get_catalogue_data(storage)
    
    results = []
    
    q_lower = q.lower() if q else None
    cat_lower = category.lower() if category else None
    lang_lower = language.lower() if language else None
    sec_lower = section.lower() if section else None

    for sec in catalogue.get("sections", []):
        if sec_lower and sec["name"].lower() != sec_lower:
            continue
            
        for show in sec.get("shows", []):
            if cat_lower and not any(c.lower() == cat_lower for c in show.get("categories", [])):
                continue
                
            # Filter seasons and episodes based on language
            filtered_seasons = []
            for season in show.get("seasons", []):
                filtered_eps = []
                for ep in season.get("episodes", []):
                    if lang_lower and lang_lower not in [l.lower() for l in ep.get("languages", [])]:
                        continue
                    filtered_eps.append(ep)
                if filtered_eps:
                    filtered_seasons.append({**season, "episodes": filtered_eps})
                    
            if lang_lower and not filtered_seasons:
                continue
                
            # Filter trailers
            filtered_trailers = []
            for trailer in show.get("trailers", []):
                if lang_lower and lang_lower not in [l.lower() for l in trailer.get("languages", [])]:
                    continue
                filtered_trailers.append(trailer)
                
            if lang_lower and not filtered_seasons and not filtered_trailers:
                continue
                
            # Apply `q` query
            match_q = False
            if not q_lower:
                match_q = True
            else:
                if q_lower in show.get("title", "").lower():
                    match_q = True
                elif any(q_lower in c.lower() for c in show.get("categories", [])):
                    match_q = True
                else:
                    for s in filtered_seasons:
                        if any(q_lower in e.get("title", "").lower() for e in s["episodes"]):
                            match_q = True
                            break
                    if not match_q:
                        for t in filtered_trailers:
                            if q_lower in t.get("title", "").lower():
                                match_q = True
                                break
                                
            if match_q:
                # Return the matching show with its filtered seasons/trailers
                matched_show = {**show, "seasons": filtered_seasons, "trailers": filtered_trailers}
                results.append(matched_show)

    return {"results": results}
