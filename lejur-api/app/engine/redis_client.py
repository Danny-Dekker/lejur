from typing import Optional
import redis
from app.core.config import settings

_redis: Optional[redis.Redis] = None

def get_redis() -> Optional[redis.Redis]:
    global _redis
    if not settings.REDIS_URL:
        return None
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis
