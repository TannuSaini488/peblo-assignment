from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
import json

from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.models.publish_run import PublishRun
from app.storage.base import StorageBackend
from app.services.validation_service import generate_validation_report
from app.schemas.catalogue import (
    Catalogue, CatalogueSection, CatalogueShow, CatalogueSeason, 
    CatalogueEpisode, CatalogueTrailer, CatalogueArtwork
)

async def publish_catalogue(db: AsyncSession, storage: StorageBackend, user_id: str) -> PublishRun:
    """
    1. Validates publish-blocking data.
    2. Builds catalogue.
    3. Writes to storage atomically.
    4. Records the run.
    """
    # 1. Validate
    report = await generate_validation_report(db)
    if report.blocking_errors:
        raise Exception("Publish blocked by validation errors")

    # 2. Build Catalogue
    result = await db.execute(
        select(Show)
        .options(
            selectinload(Show.seasons).selectinload(Season.episodes).selectinload(Episode.artwork)
        )
        .where(Show.status == "published")
        .order_by(Show.title) # Deterministic ordering
    )
    shows = result.scalars().all()

    sections_map = {}
    total_episodes = 0
    total_shows = len(shows)

    for show in shows:
        section_name = show.section
        if section_name not in sections_map:
            sections_map[section_name] = []

        catalogue_seasons = []
        catalogue_trailers = []
        
        # Sort seasons deterministically
        sorted_seasons = sorted(show.seasons, key=lambda s: s.season_number)

        for season in sorted_seasons:
            # Group episodes by content_group
            grouped_episodes = {}
            for episode in season.episodes:
                if episode.status != "published":
                    continue
                cg = episode.content_group
                if cg not in grouped_episodes:
                    grouped_episodes[cg] = []
                grouped_episodes[cg].append(episode)

            # Build episodes
            season_episodes = []
            for cg, episodes in grouped_episodes.items():
                total_episodes += 1
                # Sort languages deterministically
                sorted_episodes = sorted(episodes, key=lambda e: e.language)
                base_ep = sorted_episodes[0] # Take first as base for title/duration/artwork
                
                artwork_obj = CatalogueArtwork()
                for art in base_ep.artwork:
                    url = await storage.get_url(art.storage_key)
                    setattr(artwork_obj, art.artwork_type, url)

                ep_data = {
                    "title": base_ep.episode_title,
                    "duration_seconds": base_ep.duration_seconds or 0,
                    "languages": [e.language for e in sorted_episodes],
                    "artwork": artwork_obj
                }

                if season.season_number == 0:
                    catalogue_trailers.append(CatalogueTrailer(**ep_data))
                else:
                    ep_data["episode_number"] = base_ep.episode_number
                    ep_data["content_group"] = cg
                    season_episodes.append(CatalogueEpisode(**ep_data))

            if season.season_number != 0 and season_episodes:
                # Sort episodes deterministically
                season_episodes.sort(key=lambda e: e.episode_number)
                catalogue_seasons.append(CatalogueSeason(
                    season_number=season.season_number,
                    episodes=season_episodes
                ))

        show_artwork = CatalogueArtwork()
        # Fallback artwork logic: use artwork from first episode/trailer if needed, or we assume show doesn't have artwork model directly (in seed, artwork is on episodes)
        # We can extract a poster/banner from one of the episodes for the show level if required, but usually catalogue maps this.
        # Let's take from season 1 episode 1 or trailer.
        if catalogue_seasons and catalogue_seasons[0].episodes:
            show_artwork = catalogue_seasons[0].episodes[0].artwork
        elif catalogue_trailers:
            show_artwork = catalogue_trailers[0].artwork

        cat_show = CatalogueShow(
            id=str(show.id),
            title=show.title,
            slug=show.slug,
            synopsis=show.synopsis,
            categories=show.categories,
            artwork=show_artwork,
            seasons=catalogue_seasons,
            trailers=catalogue_trailers
        )
        sections_map[section_name].append(cat_show)

    # Convert to sections list, sorted by section name
    catalogue_sections = []
    for section_name in sorted(sections_map.keys()):
        catalogue_sections.append(CatalogueSection(
            name=section_name,
            shows=sections_map[section_name]
        ))

    catalogue = Catalogue(
        published_at=datetime.now(timezone.utc).isoformat(),
        sections=catalogue_sections
    )

    # 3. Write Atomically
    catalogue_json = catalogue.model_dump_json(exclude_none=True).encode('utf-8')
    final_key = "catalogue.json"
    
    try:
        await storage.put_atomic(final_key, catalogue_json, "application/json")
        outcome = "success"
        error_msg = None
    except Exception as e:
        outcome = "failure"
        error_msg = str(e)

    # 4. Record Run
    run = PublishRun(
        published_by=user_id,
        show_count=total_shows,
        episode_count=total_episodes,
        catalogue_key=final_key if outcome == "success" else None,
        outcome=outcome,
        error_message=error_msg
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    if outcome == "failure":
        raise Exception(f"Publish failed to write to storage: {error_msg}")

    return run
