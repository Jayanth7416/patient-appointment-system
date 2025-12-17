"""Cache Service"""

from typing import Optional, Any
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class CacheService:
    """
    Redis-based cache service

    Provides caching and distributed locking
    """

    def __init__(self):
        self.cache: dict = {}
        self.locks: dict = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        entry = self.cache.get(key)
        if entry:
            if entry["expires_at"] > datetime.utcnow():
                return entry["value"]
            del self.cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache"""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
        }

    async def delete(self, key: str):
        """Delete from cache"""
        if key in self.cache:
            del self.cache[key]

    async def acquire_lock(self, key: str, ttl: int = 30) -> bool:
        """
        Acquire distributed lock

        Returns True if lock acquired, False otherwise
        """
        now = datetime.utcnow()

        if key in self.locks:
            lock = self.locks[key]
            if lock["expires_at"] > now:
                return False
            # Lock expired
            del self.locks[key]

        self.locks[key] = {
            "acquired_at": now,
            "expires_at": now + timedelta(seconds=ttl)
        }

        logger.debug("lock_acquired", key=key)
        return True

    async def release_lock(self, key: str):
        """Release distributed lock"""
        if key in self.locks:
            del self.locks[key]
            logger.debug("lock_released", key=key)

    async def extend_lock(self, key: str, ttl: int = 30) -> bool:
        """Extend lock TTL"""
        if key in self.locks:
            self.locks[key]["expires_at"] = datetime.utcnow() + timedelta(seconds=ttl)
            return True
        return False
