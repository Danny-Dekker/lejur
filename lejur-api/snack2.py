from datetime import date
from app.db import SessionLocal
from app.models.org import Org
from app.models.account import Account, CoreType, NormalSide
from app.models.journal import JournalEntry, JournalLine, LineSide

db = SessionLocal()
try:
    org = Org(name="Lejur Demo Co")
    db.add(org); db.flush()

    cash = Account(org_id=org.id, code="1000", name="Cash",
                   core_type=CoreType.ASSET, normal_side=NormalSide.DEBIT)
    revenue = Account(org_id=org.id, code="4000", name="Revenue",
                      core_type=CoreType.INCOME, normal_side=NormalSide.CREDIT)
    db.add_all([cash, revenue]); db.flush()

    je = JournalEntry(org_id=org.id, date=date.today(), memo="Seed sale")
    db.add(je); db.flush()

    db.add_all([
        JournalLine(entry_id=je.id, org_id=org.id, account_id=cash.id,
                    side=LineSide.DEBIT,  amount=100.00, description="Cash received"),
        JournalLine(entry_id=je.id, org_id=org.id, account_id=revenue.id,
                    side=LineSide.CREDIT, amount=100.00, description="Sales revenue"),
    ])

    db.commit()
    print("OK:", {"org": org.id, "entry": je.id})
finally:
    db.close()
