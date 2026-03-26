from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Settings

engine = create_engine(Settings.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()