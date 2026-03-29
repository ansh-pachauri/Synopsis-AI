from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.base import Base  # noqa: F401 — re-exported for convenience

engine = create_engine(settings().DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()