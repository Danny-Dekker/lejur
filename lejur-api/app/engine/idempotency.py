from typing import Optional
import hashlib
from app.engine.redis_client import get_redis
from app.core.config import settings

IDEMP_PREFIX = "idem:je:"

def idem_key(raw: str) -> str:
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{IDEMP_PREFIX}{h}"

def check_and_set_idem(raw: str) -> Optional[str]:
    r = get_redis()
    if r is None:
        return None
    key = idem_key(raw)
    ok = r.set(key, "1", nx=True, ex=settings.IDEMPOTENCY_TTL)
    return key if ok else None
