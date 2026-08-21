import shutil
from pathlib import Path

import pytest

from app.storage.local import LocalStorageBackend


@pytest.mark.asyncio
async def test_local_put_atomic_replaces_complete_catalogue():
    temp_dir = Path('test_storage_tmp')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    try:
        storage = LocalStorageBackend(str(temp_dir))

        await storage.put_atomic('catalogue.json', b'{"version":1}', 'application/json')
        await storage.put_atomic('catalogue.json', b'{"version":2}', 'application/json')

        assert await storage.get('catalogue.json') == b'{"version":2}'
        assert list(temp_dir.glob('catalogue.json.tmp.*')) == []
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
