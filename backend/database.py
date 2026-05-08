"""
MedEdge — Database Setup (SQLModel + SQLite)
Drop-in PostgreSQL-ready: just change DATABASE_URL in .env.
"""
from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
