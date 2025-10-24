from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.journal import JournalEntry, JournalLine, LineSide
from datetime import date

class ReversalError(Exception):
    pass

def reverse_entry(db: Session, entry_id: int, reversal_date: date, memo_prefix: str = "Reversal of ") -> Tuple[JournalEntry, int]:
    # Load original
    orig = db.execute(
        select(JournalEntry).where(JournalEntry.id == entry_id)
    ).scalar_one_or_none()
    if not orig:
        raise ReversalError(f"Entry {entry_id} not found")

    # Load lines
    lines = db.execute(
        select(JournalLine).where(JournalLine.entry_id == entry_id)
    ).scalars().all()
    if not lines:
        raise ReversalError(f"Entry {entry_id} has no lines")

    # Create reversing entry
    rev = JournalEntry(
        org_id=orig.org_id,
        date=reversal_date,
        memo=(memo_prefix + (orig.memo or f"JE#{orig.id}")),
        created_by=orig.created_by,
    )
    db.add(rev)
    db.flush()

    for ln in lines:
        db.add(JournalLine(
            entry_id=rev.id,
            org_id=orig.org_id,
            account_id=ln.account_id,
            side=LineSide.DEBIT if ln.side == LineSide.CREDIT else LineSide.CREDIT,
            amount=ln.amount,
            description=f"Reversal of line {ln.id}",
        ))

    db.commit()
    db.refresh(rev)
    return rev, rev.id
