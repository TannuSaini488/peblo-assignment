import json
import uuid
from types import SimpleNamespace

import pytest

from app.schemas.publish import ValidationError, ValidationReport
from app.services import publish_service


class FakeResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return self

    def all(self):
        return self.items


class FakeDb:
    def __init__(self, shows):
        self.shows = shows
        self.added = []
        self.commits = 0

    async def execute(self, _query):
        return FakeResult(self.shows)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.commits += 1

    async def refresh(self, item):
        if not getattr(item, 'id', None):
            item.id = uuid.uuid4()


class FakeStorage:
    def __init__(self):
        self.data = None
        self.final_key = None
        self.urls = []

    async def get_url(self, key):
        self.urls.append(key)
        return f'/storage/{key}'

    async def put_atomic(self, final_key, data, content_type):
        self.final_key = final_key
        self.data = data
        self.content_type = content_type
        return final_key


def art(artwork_type, key):
    return SimpleNamespace(artwork_type=artwork_type, storage_key=key)


def episode(number, title, content_group, language, status='published'):
    return SimpleNamespace(
        episode_number=number,
        episode_title=title,
        content_group=content_group,
        language=language,
        status=status,
        duration_seconds=120,
        artwork=[
            art('poster', f'{content_group}-{language}-poster.jpg'),
            art('banner', f'{content_group}-{language}-banner.jpg'),
            art('thumbnail', f'{content_group}-{language}-thumbnail.jpg'),
        ],
    )


def season(number, episodes):
    return SimpleNamespace(season_number=number, episodes=episodes)


def show(title, seasons):
    return SimpleNamespace(
        id=uuid.uuid4(),
        title=title,
        slug=title.lower().replace(' ', '-'),
        synopsis=f'{title} synopsis',
        categories=['learning'],
        section='series',
        seasons=seasons,
    )


@pytest.mark.asyncio
async def test_publish_collapses_content_group_languages_and_excludes_season_zero(monkeypatch):
    async def no_errors(_db):
        return ValidationReport(blocking_errors=[], warnings=[])

    monkeypatch.setattr(publish_service, 'generate_validation_report', no_errors)
    storage = FakeStorage()
    db = FakeDb([
        show('Zoo Maths', [
            season(1, [
                episode(2, 'Second', 'zoo-s01e02', 'en'),
                episode(1, 'First Hindi', 'zoo-s01e01', 'hi'),
                episode(1, 'First English', 'zoo-s01e01', 'en'),
            ]),
            season(0, [episode(1, 'Trailer', 'zoo-trailer', 'en')]),
        ])
    ])

    await publish_service.publish_catalogue(db, storage, str(uuid.uuid4()))

    catalogue = json.loads(storage.data.decode('utf-8'))
    published_show = catalogue['sections'][0]['shows'][0]

    assert storage.final_key == 'catalogue.json'
    assert published_show['trailers'][0]['title'] == 'Trailer'
    assert [s['season_number'] for s in published_show['seasons']] == [1]
    assert [e['episode_number'] for e in published_show['seasons'][0]['episodes']] == [1, 2]
    first_episode = published_show['seasons'][0]['episodes'][0]
    assert first_episode['content_group'] == 'zoo-s01e01'
    assert first_episode['languages'] == ['en', 'hi']


@pytest.mark.asyncio
async def test_publish_blocks_when_validation_has_errors(monkeypatch):
    async def blocked(_db):
        return ValidationReport(
            blocking_errors=[ValidationError(
                show_id=uuid.uuid4(),
                show_title='Broken Show',
                error_type='missing_artwork',
                message='Episode is missing artwork.',
            )],
            warnings=[],
        )

    monkeypatch.setattr(publish_service, 'generate_validation_report', blocked)
    storage = FakeStorage()

    with pytest.raises(Exception, match='Publish blocked'):
        await publish_service.publish_catalogue(FakeDb([]), storage, str(uuid.uuid4()))

    assert storage.data is None
