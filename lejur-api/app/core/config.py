from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]  # .../lejur-api
load_dotenv(ROOT_DIR / ".env")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    IDEMPOTENCY_TTL: int = int(os.getenv("IDEMPOTENCY_TTL", "86400"))
    TB_CACHE_TTL: int = int(os.getenv("TB_CACHE_TTL", "60"))

settings = Settings()
