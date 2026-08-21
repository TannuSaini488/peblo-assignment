import pytest

from app.routers import catalog


CATALOGUE = {
    'sections': [
        {
            'name': 'series',
            'shows': [
                {
                    'id': 'show-1',
                    'title': 'Moti Learns Maths',
                    'categories': ['maths', 'learning'],
                    'seasons': [
                        {'season_number': 1, 'episodes': [
                            {'title': 'Counting Kites', 'languages': ['en', 'hi']},
                            {'title': 'Only English', 'languages': ['en']},
                        ]}
                    ],
                    'trailers': [],
                }
            ],
        },
        {
            'name': 'songs',
            'shows': [
                {
                    'id': 'show-2',
                    'title': 'Peblo Songs',
                    'categories': ['music'],
                    'seasons': [
                        {'season_number': 1, 'episodes': [
                            {'title': 'Hello Song', 'languages': ['en']},
                        ]}
                    ],
                    'trailers': [],
                }
            ],
        },
    ]
}


@pytest.mark.asyncio
async def test_catalog_search_filters_compose(monkeypatch):
    async def fake_catalogue(_storage):
        return CATALOGUE

    monkeypatch.setattr(catalog, 'get_catalogue_data', fake_catalogue)

    result = await catalog.search_catalog(q='kites', category='maths', language='hi', section='series', storage=None)

    assert [show['id'] for show in result['results']] == ['show-1']
    assert result['results'][0]['seasons'][0]['episodes'][0]['title'] == 'Counting Kites'


@pytest.mark.asyncio
async def test_catalog_search_returns_empty_when_composed_filter_excludes(monkeypatch):
    async def fake_catalogue(_storage):
        return CATALOGUE

    monkeypatch.setattr(catalog, 'get_catalogue_data', fake_catalogue)

    result = await catalog.search_catalog(q='kites', category='music', language='hi', section='series', storage=None)

    assert result['results'] == []
