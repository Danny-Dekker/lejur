from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..engine.drafts import clear_draft, load_draft, save_draft
from ..engine.posting import PostingError, post_entry
from ..engine.reversal import ReversalError, reverse_entry
from ..engine.trial_balance import trial_balance
from ..models.account import Account
from ..models.journal import JournalEntry
from ..schemas.journal import JournalEntryIn

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

@router.post("/journal-entries")
def create_journal_entry(payload: JournalEntryIn, db: Session = Depends(get_db)):
    try:
        je, _ = post_entry(db, payload)
        # Invalidate TB cache for this org
        try:
            from ..engine.redis_client import get_redis
            r = get_redis()
            if r is not None:
                r.delete(f"tb:{payload.org_id}")
        except Exception:
            pass
        return {"id": je.id, "org_id": je.org_id, "date": str(je.date)}
    except PostingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trial-balance/{org_id}")
def api_trial_balance(org_id: int, db: Session = Depends(get_db)):
    return trial_balance(db, org_id)

@router.get("/accounts/{org_id}")
def list_accounts(org_id: int, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Account).where(Account.org_id == org_id).order_by(Account.code)
        )
        .scalars()
        .all()
    )
    return rows

@router.get("/journals/{org_id}")
def list_journals(org_id: int, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(JournalEntry)
            .where(JournalEntry.org_id == org_id)
            .order_by(JournalEntry.date.desc(), JournalEntry.id.desc())
            .limit(100)
        )
        .scalars()
        .all()
    )
    return rows

@router.post("/drafts/{org_id}/{user_id}")
def api_save_draft(org_id: int, user_id: int, draft: dict):
    k = save_draft(org_id, user_id, draft)
    return {"ok": True, "key": k}

@router.get("/drafts/{org_id}/{user_id}")
def api_load_draft(org_id: int, user_id: int):
    d = load_draft(org_id, user_id)
    return {"draft": d}

@router.delete("/drafts/{org_id}/{user_id}")
def api_clear_draft(org_id: int, user_id: int):
    clear_draft(org_id, user_id)
    return {"ok": True}

@router.post("/journal-entries/{entry_id}/reverse")
def api_reverse_entry(entry_id: int, reversal_date: date, db: Session = Depends(get_db)):
    try:
        rev, _ = reverse_entry(db, entry_id, reversal_date)
        # bust TB cache
        try:
            from ..engine.redis_client import get_redis
            r = get_redis()
            if r is not None:
                r.delete(f"tb:{rev.org_id}")
        except Exception:
            pass
        return {"reversal_id": rev.id, "org_id": rev.org_id, "date": str(rev.date)}
    except ReversalError as e:
        raise HTTPException(status_code=404, detail=str(e))
