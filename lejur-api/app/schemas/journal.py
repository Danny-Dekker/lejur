from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class JournalLineIn(BaseModel):
    account_id: int
    side: str  # "DEBIT" | "CREDIT"
    amount: Decimal = Field(gt=0)
    description: Optional[str] = None

class JournalEntryIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    org_id: int
    date: date
    memo: Optional[str] = None
    created_by: Optional[int] = None
    lines: List[JournalLineIn]
    idempotency_key: Optional[str] = None
