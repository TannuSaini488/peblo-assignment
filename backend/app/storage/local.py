import os
import shutil
import uuid
import aiofiles
from app.storage.base import StorageBackend

class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_abs_path(self, key: str) -> str:
        return os.path.join(self.base_path, key)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        path = self._get_abs_path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        async with aiofiles.open(path, 'wb') as f:
            await f.write(data)
        return key

    async def get(self, key: str) -> bytes:
        path = self._get_abs_path(key)
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        path = self._get_abs_path(key)
        if os.path.exists(path):
            os.remove(path)

    async def get_url(self, key: str) -> str:
        # We assume FastAPI will serve self.base_path mounted at /storage
        return f"/storage/{key}"

    async def put_atomic(self, final_key: str, data: bytes, content_type: str) -> str:
        temp_key = f"{final_key}.tmp.{uuid.uuid4()}"
        temp_path = self._get_abs_path(temp_key)
        final_path = self._get_abs_path(final_key)
        
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        
        # Write to temp file
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(data)
            
        # Atomically replace final file
        os.replace(temp_path, final_path)
        return final_key
