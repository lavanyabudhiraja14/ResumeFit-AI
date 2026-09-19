"""Lightweight in-memory cache for live job feeds to prevent hammering public endpoints."""

import time
import threading
from typing import Any, Dict, Optional, Tuple
from app.core.config import settings


class JobCache:
    _instance: Optional["JobCache"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "JobCache":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._store: Dict[str, Tuple[float, float, Any]] = {}
                cls._instance._store_lock = threading.Lock()
            return cls._instance

    def get(self, key: str) -> Optional[Any]:
        with self._store_lock:
            entry = self._store.get(key)
            if not entry:
                return None
            created_at, ttl, data = entry
            if (time.time() - created_at) > ttl:
                # Expired
                del self._store[key]
                return None
            return data

    def set(self, key: str, data: Any, ttl: Optional[float] = None) -> None:
        effective_ttl = ttl if ttl is not None else float(settings.JOB_CACHE_TTL_SECONDS)
        with self._store_lock:
            self._store[key] = (time.time(), effective_ttl, data)

    def clear(self) -> None:
        with self._store_lock:
            self._store.clear()


# Global singleton instance
job_cache = JobCache()
