import uuid
from types import SimpleNamespace

import pytest

from app.services.validation_service import generate_validation_report


class FakeResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return self

    def all(self):
        return self.items


class FakeDb:
    async def execute(self, _query):
        show_id = uuid.uuid4()
        season_id = uuid.uuid4()
        episode_id = uuid.uuid4()
        episode = SimpleNamespace(
            id=episode_id,
            episode_title='Missing Duration',
            status='published',
            duration_seconds=None,
            language='en',
            artwork=[],
        )
        season = SimpleNamespace(id=season_id, season_number=1, episodes=[episode])
        show = SimpleNamespace(
            id=show_id,
            title='Broken Published Show',
            section=None,
            categories=['learning'],
            seasons=[season],
        )
        return FakeResult([show])


@pytest.mark.asyncio
async def test_validation_report_groups_publish_blocking_issues():
    report = await generate_validation_report(FakeDb())

    error_types = {error.error_type for error in report.blocking_errors}
    assert {'missing_section', 'missing_duration', 'missing_artwork'} <= error_types
    assert any(error.show_title == 'Broken Published Show' for error in report.blocking_errors)
