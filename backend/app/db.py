from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# SQLite file will be created at runtime in the repository (./backend/data.db)
DATABASE_URL = "sqlite:///./backend/data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
