from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import Integer, String, Date, DateTime, Numeric, ForeignKey, Enum, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class LineSide(PyEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    memo: Mapped[Optional[str]] = mapped_column(String(240))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    posted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[List["JournalLine"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_journal_entries_org_date", "org_id", "date"),)

class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id", ondelete="CASCADE"), index=True, nullable=False)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), index=True, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True, nullable=False)

    side: Mapped[LineSide] = mapped_column(Enum(LineSide, name="line_side"), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(240))

    entry: Mapped["JournalEntry"] = relationship(back_populates="lines")
