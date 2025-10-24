from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.account import Account, NormalSide
from app.models.journal import JournalLine, LineSide
from app.engine.redis_client import get_redis
from app.core.config import settings
import json

def trial_balance(db: Session, org_id: int) -> Dict[str, Any]:
    r = get_redis()
    cache_key = f"tb:{org_id}"
    if r is not None:
        cached = r.get(cache_key)
        if cached:
            return json.loads(cached)

    amt = case(
        (JournalLine.side == LineSide.DEBIT, JournalLine.amount),
        (JournalLine.side == LineSide.CREDIT, -JournalLine.amount),
        else_=0,
    )

    rows = (
        db.query(
            Account.id.label("account_id"),
            Account.code, Account.name, Account.normal_side,
            func.coalesce(func.sum(amt), 0).label("balance")
        )
        .outerjoin(JournalLine, (JournalLine.account_id == Account.id) & (JournalLine.org_id == org_id))
        .filter(Account.org_id == org_id)
        .group_by(Account.id, Account.code, Account.name, Account.normal_side)
        .order_by(Account.code)
        .all()
    )

    total_debits = sum(rw.balance for rw in rows if rw.normal_side == NormalSide.DEBIT)
    total_credits = -sum(rw.balance for rw in rows if rw.normal_side == NormalSide.CREDIT)
    balanced = round(float(total_debits - total_credits), 2) == 0.0

    payload = {
        "org_id": org_id,
        "balanced": balanced,
        "totals": {"debits": float(total_debits), "credits": float(total_credits)},
        "lines": [
            {
                "account_id": rw.account_id,
                "code": rw.code,
                "name": rw.name,
                "normal_side": rw.normal_side.value,
                "balance": float(rw.balance),
            }
            for rw in rows
        ],
    }

    if r is not None:
        r.setex(cache_key, settings.TB_CACHE_TTL, json.dumps(payload))

    return payload
