from app.db import SessionLocal
from app.models.account import Account, CoreType, NormalSide

def ensure(db, org_id, code, name, core_type, normal_side, is_postable=True, parent_id=None):
    row = db.query(Account).filter(Account.org_id == org_id, Account.code == code).first()
    if row:
        return row
    row = Account(
        org_id=org_id, code=code, name=name,
        core_type=core_type, normal_side=normal_side,
        is_postable=is_postable, parent_id=parent_id
    )
    db.add(row); db.flush()
    return row

def run(org_id: int):
    db = SessionLocal()
    try:
        # Assets
        cash = ensure(db, org_id, "1000", "Cash", CoreType.ASSET, NormalSide.DEBIT)
        ar   = ensure(db, org_id, "1100", "Accounts Receivable", CoreType.ASSET, NormalSide.DEBIT)
        inv  = ensure(db, org_id, "1200", "Inventory", CoreType.ASSET, NormalSide.DEBIT)

        # Liabilities
        ap   = ensure(db, org_id, "2000", "Accounts Payable", CoreType.LIABILITY, NormalSide.CREDIT)
        tax  = ensure(db, org_id, "2100", "Sales Tax Payable", CoreType.LIABILITY, NormalSide.CREDIT)

        # Equity
        equity = ensure(db, org_id, "3000", "Owner's Equity", CoreType.EQUITY, NormalSide.CREDIT)

        # Income
        sales = ensure(db, org_id, "4000", "Sales Revenue", CoreType.INCOME, NormalSide.CREDIT)

        # COGS + Expenses
        cogs = ensure(db, org_id, "5000", "Cost of Goods Sold", CoreType.EXPENSE, NormalSide.DEBIT)
        rent = ensure(db, org_id, "6000", "Rent Expense", CoreType.EXPENSE, NormalSide.DEBIT)
        util = ensure(db, org_id, "6100", "Utilities Expense", CoreType.EXPENSE, NormalSide.DEBIT)

        db.commit()
        print("Seeded COA for org:", org_id)
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_coa.py <org_id>")
        sys.exit(1)
    run(int(sys.argv[1]))
