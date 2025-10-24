from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import Integer, String, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class CoreType(PyEnum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class NormalSide(PyEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), index=True, nullable=False)

    code: Mapped[str] = mapped_column(String(24), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    is_postable: Mapped[bool] = mapped_column(Boolean, default=True)

    core_type: Mapped[CoreType] = mapped_column(Enum(CoreType, name="core_type"), nullable=False)
    normal_side: Mapped[NormalSide] = mapped_column(Enum(NormalSide, name="normal_side"), nullable=False)

    is_contra: Mapped[bool] = mapped_column(Boolean, default=False)

    parent: Mapped[Optional["Account"]] = relationship(remote_side="Account.id")

    __table_args__ = (
        UniqueConstraint("org_id", "code", name="uq_account_org_code"),
        UniqueConstraint("org_id", "name", name="uq_account_org_name"),
    )
