from typing import Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.account import Account
from app.models.journal import JournalEntry, JournalLine, LineSide
from app.schemas.journal import JournalEntryIn
from app.engine.idempotency import check_and_set_idem
from app.engine.redis_client import get_redis

class PostingError(Exception):
    pass

def _sum_with_sign(lines) -> Decimal:
    total = Decimal("0")
    for ln in lines:
        amt = Decimal(ln.amount)
        if ln.side.upper() == "DEBIT":
            total += amt
        elif ln.side.upper() == "CREDIT":
            total -= amt
        else:
            raise PostingError(f"Invalid side: {ln.side}")
    return total

def _ensure_accounts_postable(db: Session, org_id: int, account_ids: list) -> None:
    rows = db.execute(select(Account.id, Account.is_postable, Account.org_id)
                      .where(Account.id.in_(account_ids))).all()
    found = {r.id: (r.is_postable, r.org_id) for r in rows}
    missing = [aid for aid in account_ids if aid not in found]
    if missing:
        raise PostingError(f"Accounts not found: {missing}")
    cross = [aid for aid, (_post, acc_org) in found.items() if acc_org != org_id]
    if cross:
        raise PostingError(f"Accounts not in org: {cross}")
    bad = [aid for aid, (is_postable, _org) in found.items() if not is_postable]
    if bad:
        raise PostingError(f"Non-postable accounts: {bad}")

def post_entry(db: Session, data: JournalEntryIn) -> Tuple[JournalEntry, int]:
    # Idempotency
    raw_key = data.idempotency_key or f"{data.org_id}|{data.date}|{data.memo}|" + \
              "|".join(f"{ln.account_id}:{ln.side}:{ln.amount}" for ln in data.lines)
    idem_hit = check_and_set_idem(raw_key)
    if idem_hit is None and get_redis() is not None:
        raise PostingError("Duplicate idempotency key: possible re-submit")

    if not data.lines or len(data.lines) < 2:
        raise PostingError("Entry requires at least two lines")

    total = _sum_with_sign(data.lines)
    if total != 0:
        raise PostingError(f"Entry not balanced (net={total})")

    _ensure_accounts_postable(db, data.org_id, [ln.account_id for ln in data.lines])

    je = JournalEntry(org_id=data.org_id, date=data.date, memo=data.memo, created_by=data.created_by)
    db.add(je)
    db.flush()

    for ln in data.lines:
        jl = JournalLine(
            entry_id=je.id,
            org_id=data.org_id,
            account_id=ln.account_id,
            side=LineSide.DEBIT if ln.side.upper() == "DEBIT" else LineSide.CREDIT,
            amount=ln.amount,
            description=ln.description,
        )
        db.add(jl)

    db.commit()
    db.refresh(je)
    return je, je.id
