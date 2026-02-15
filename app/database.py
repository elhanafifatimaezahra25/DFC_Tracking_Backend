from sqlmodel import create_engine, SQLModel
from .core.config import settings
from sqlmodel import Session

DATABASE_URL = settings.DATABASE_URL
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def init_db():
    # Import all model modules so SQLModel metadata includes their tables
    # (imports are local to avoid import-time side effects elsewhere)
    from .models import user, dfc, reference  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that yields a database session."""
    with Session(engine) as session:
        yield session
