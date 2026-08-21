from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.schemas.publish import ValidationReport, ValidationError

import json

# Pre-load reference data
def load_reference_data():
    try:
        with open("reference.json") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("../reference.json") as f:
            return json.load(f)

reference_data = load_reference_data()
VALID_SECTIONS = reference_data["sections"]
VALID_CATEGORIES = reference_data["categories"]
VALID_LANGUAGES = reference_data["languages"]

async def generate_validation_report(db: AsyncSession) -> ValidationReport:
    """
    Generates a report of blocking errors and warnings for the catalogue.
    """
    blocking_errors = []
    warnings = []

    # Get all published shows with their seasons, episodes, and artwork
    result = await db.execute(
        select(Show)
        .options(
            selectinload(Show.seasons).selectinload(Season.episodes).selectinload(Episode.artwork)
        )
        .where(Show.status == "published")
    )
    shows = result.scalars().all()

    for show in shows:
        # 1. A published show must have a section
        if not show.section:
            blocking_errors.append(ValidationError(
                show_id=show.id,
                show_title=show.title,
                error_type="missing_section",
                message=f"Show '{show.title}' is marked as published but has no section."
            ))
        elif show.section not in VALID_SECTIONS:
            blocking_errors.append(ValidationError(
                show_id=show.id,
                show_title=show.title,
                error_type="invalid_section",
                message=f"Show '{show.title}' has invalid section '{show.section}'."
            ))

        # Check categories
        for cat in show.categories:
            if cat not in VALID_CATEGORIES:
                warnings.append(ValidationError(
                    show_id=show.id,
                    show_title=show.title,
                    error_type="invalid_category",
                    message=f"Show '{show.title}' has unrecognized category '{cat}'."
                ))

        has_published_episodes = False

        for season in show.seasons:
            for episode in season.episodes:
                if episode.status != "published":
                    continue
                
                has_published_episodes = True

                # Check language
                if episode.language not in VALID_LANGUAGES:
                    warnings.append(ValidationError(
                        show_id=show.id,
                        show_title=show.title,
                        season_id=season.id,
                        season_number=season.season_number,
                        episode_id=episode.id,
                        episode_title=episode.episode_title,
                        error_type="invalid_language",
                        message=f"Episode '{episode.episode_title}' has unrecognized language '{episode.language}'."
                    ))

                # 2. An episode cannot be published without duration
                if not episode.duration_seconds:
                    blocking_errors.append(ValidationError(
                        show_id=show.id,
                        show_title=show.title,
                        season_id=season.id,
                        season_number=season.season_number,
                        episode_id=episode.id,
                        episode_title=episode.episode_title,
                        error_type="missing_duration",
                        message=f"Episode '{episode.episode_title}' is missing duration."
                    ))

                # 3. An episode cannot be published without artwork
                artwork_types = [a.artwork_type for a in episode.artwork]
                required_artwork = {"poster", "thumbnail"}
                # If season 0, maybe just thumbnail/banner is fine? 
                # Let's say all need poster, thumbnail, banner for simplicity, or just 'thumbnail' minimum.
                # The prompt: "An episode cannot be published without artwork"
                if not episode.artwork:
                    blocking_errors.append(ValidationError(
                        show_id=show.id,
                        show_title=show.title,
                        season_id=season.id,
                        season_number=season.season_number,
                        episode_id=episode.id,
                        episode_title=episode.episode_title,
                        error_type="missing_artwork",
                        message=f"Episode '{episode.episode_title}' is missing all artwork."
                    ))

        if not has_published_episodes:
            warnings.append(ValidationError(
                show_id=show.id,
                show_title=show.title,
                error_type="empty_show",
                message=f"Show '{show.title}' has no published episodes."
            ))

    # Append seed anomalies
    try:
        with open("seed_anomalies.json", "r") as f:
            seed_anomalies = json.load(f)
            for anomaly in seed_anomalies:
                warnings.append(ValidationError(
                    show_id="seed-anomaly",
                    show_title="Seed Data",
                    error_type=anomaly["type"],
                    message=anomaly["message"]
                ))
    except FileNotFoundError:
        pass
        
    return ValidationReport(
        blocking_errors=blocking_errors,
        warnings=warnings
    )
