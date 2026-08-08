"""Thin Redis wrapper. All callers must treat Redis as optional — if it's
unreachable, functions return None/no-op rather than raising, since Redis is
only used for caching/rate-limit backing, never as the source of truth."""
import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[redis.Redis] = None
_unavailable = False


def get_redis_client() -> Optional[redis.Redis]:
    global _client, _unavailable
    if _unavailable:
        return None
    if _client is None:
        try:
            _client = redis.Redis.from_url(
                settings.REDIS_URL,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
                retry_on_timeout=False,
                health_check_interval=None,
            )
            _client.ping()
        except Exception as e:
            logger.warning("Redis unavailable: %s", e)
            _client = None
            _unavailable = True
    return _client


def cache_get(key: str) -> Optional[Any]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.warning("Redis GET failed for %s: %s", key, e)
        return None


def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.setex(key, ttl_seconds, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning("Redis SET failed for %s: %s", key, e)
        return False


def cache_delete(key: str) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception as e:
        logger.warning("Redis DELETE failed for %s: %s", key, e)
        return False
