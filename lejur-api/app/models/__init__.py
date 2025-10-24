from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

# Register models for Alembic discovery
from .user import User  # noqa: F401
from .org import Org, OrgUser  # noqa: F401
from .account import Account  # noqa: F401
from .journal import JournalEntry, JournalLine  # noqa: F401
