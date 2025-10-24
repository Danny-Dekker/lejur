from app.db import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    u = User(email="test@example.com", name="Testy")
    db.add(u)
    db.commit()
    db.refresh(u)
    print("Inserted user id:", u.id)
finally:
    db.close()
