import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "db"
DB_PORT = os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432"
DB_USER = os.getenv("POSTGRES_USER") or os.getenv("DB_USER") or "postgres"
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD") or "postgres"
DB_NAME = os.getenv("POSTGRES_DB") or os.getenv("DB_NAME") or "telemedicina_db"

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)