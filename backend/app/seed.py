import asyncio
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.database import AsyncSessionLocal, engine
from app.models import Show, Season, Episode, Artwork, User
from app.services.auth_service import get_password_hash
from app.config import settings
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    async with AsyncSessionLocal() as db:
        # Check if users exist
        result = await db.execute(select(User).limit(1))
        if not result.scalars().first():
            logger.info("Seeding users...")
            admin = User(
                username=settings.default_admin_username,
                password_hash=get_password_hash(settings.default_admin_password),
                role="admin"
            )
            editor = User(
                username=settings.default_editor_username,
                password_hash=get_password_hash(settings.default_editor_password),
                role="editor"
            )
            db.add_all([admin, editor])
            await db.commit()

        # Check if shows exist
        result = await db.execute(select(Show).limit(1))
        if result.scalars().first():
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Loading seed data from seed_shows.json...")
        try:
            with open("seed_shows.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Maybe we are in backend dir, try one level up
            with open("../seed_shows.json", "r") as f:
                data = json.load(f)
        
        shows_cache = {}
        seasons_cache = {}
        seed_anomalies = []

        for item in data:
            slug = item["slug"]
            
            # Title inconsistencies checking
            show_title = item.get("show_title", "")
            if show_title.strip() != show_title:
                seed_anomalies.append({
                    "type": "title_inconsistency",
                    "message": f"Show '{slug}' has trailing spaces in title."
                })
            
            # Create show if not exists
            if slug not in shows_cache:
                show = Show(
                    title=show_title.strip(),
                    slug=slug,
                    section=item.get("section"),
                    categories=item.get("categories", []),
                    synopsis=item.get("synopsis", ""),
                    status="published" # Inferring from data
                )
                db.add(show)
                await db.commit()
                await db.refresh(show)
                shows_cache[slug] = show.id
            
            show_id = shows_cache[slug]
            
            # Create season if not exists
            season_key = (slug, item["season_number"])
            if season_key not in seasons_cache:
                season = Season(
                    show_id=show_id,
                    season_number=item["season_number"]
                )
                db.add(season)
                await db.commit()
                await db.refresh(season)
                seasons_cache[season_key] = season.id
                
            season_id = seasons_cache[season_key]
            
            # Create episode
            episode = Episode(
                season_id=season_id,
                episode_number=item["episode_number"],
                episode_title=item["episode_title"],
                duration_seconds=item.get("duration_seconds"),
                language=item["language"],
                content_group=item["content_group"],
                status=item.get("status", "published")
            )
            db.add(episode)
            
            try:
                await db.commit()
                await db.refresh(episode)
            except IntegrityError:
                await db.rollback()
                msg = f"Skipping duplicate episode '{item['episode_title']}' with content_group '{item['content_group']}' and language '{item['language']}'."
                logger.warning(msg)
                seed_anomalies.append({
                    "type": "duplicate_episode",
                    "message": msg
                })
                continue
            
            # DO NOT inject fake artwork. The validation engine MUST catch missing artwork naturally.
            # We only create artwork if we had an actual upload, but since this is seed data without actual files,
            # we will leave it empty. The user will have to fix `ep_0036` missing artwork via CMS.
            # However, if 'artwork_available' exists and is not empty, we assume the seed implies we *do* have artwork, 
            # except when it's explicitly missing like ep_0036.
            # So if we want to simulate the seed artwork, we should only do it for items that are valid.
            if "artwork_available" in item and item["artwork_available"]:
                for aw_type in item["artwork_available"]:
                    # Create mock records just so validation passes for the *good* ones.
                    # ep_0036 actually lacks 'artwork_available' or it's empty in seed.
                    artwork = Artwork(
                        episode_id=episode.id,
                        artwork_type=aw_type,
                        storage_key=f"seed_{slug}_{item['season_number']}_{item['episode_number']}_{aw_type}.jpg",
                        original_filename=f"{aw_type}.jpg",
                        width=600 if aw_type == "poster" else (1280 if aw_type == "banner" else 640),
                        height=900 if aw_type == "poster" else (720 if aw_type == "banner" else 360),
                        file_size_bytes=100000
                    )
                    db.add(artwork)
                await db.commit()
        
        # Write anomalies to a file for the validation service to read
        with open("seed_anomalies.json", "w") as f:
            json.dump(seed_anomalies, f)
            
        logger.info("Seed complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
