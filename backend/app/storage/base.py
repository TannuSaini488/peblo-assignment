from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Store data, return the storage key."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Retrieve data by key."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete data by key."""
        pass
    
    @abstractmethod
    async def get_url(self, key: str) -> str:
        """Get a URL/path to serve the stored object."""
        pass
    
    @abstractmethod
    async def put_atomic(self, final_key: str, data: bytes, content_type: str) -> str:
        """Write data atomically — readers see old or new, never partial."""
        pass
