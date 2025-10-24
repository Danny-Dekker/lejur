from typing import Optional
import json
from app.engine.redis_client import get_redis

DRAFT_PREFIX = "draft:je:"  # draft:je:{org}:{user}

def save_draft(org_id: int, user_id: int, draft: dict, ttl: int = 3600) -> Optional[str]:
    r = get_redis()
    if r is None:
        return None
    key = f"{DRAFT_PREFIX}{org_id}:{user_id}"
    r.setex(key, ttl, json.dumps(draft))
    return key

def load_draft(org_id: int, user_id: int) -> Optional[dict]:
    r = get_redis()
    if r is None:
        return None
    key = f"{DRAFT_PREFIX}{org_id}:{user_id}"
    raw = r.get(key)
    return json.loads(raw) if raw else None

def clear_draft(org_id: int, user_id: int) -> None:
    r = get_redis()
    if r is None:
        return
    r.delete(f"{DRAFT_PREFIX}{org_id}:{user_id}")
