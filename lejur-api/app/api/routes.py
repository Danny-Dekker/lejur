from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health")
def health():
    return {"ok": True, "service": "lejur-api"}

@router.get("/whoami")
def whoami():
    return {"app": "lejur", "env": "dev"}
