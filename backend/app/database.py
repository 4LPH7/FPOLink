from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")


@compiles(JSONB, "sqlite")
def _jsonb_on_sqlite(_type, _compiler, **_kw) -> str:
    """Local development on SQLite: store PostgreSQL JSONB columns as JSON text."""
    return "JSON"


engine_kwargs: dict = {"pool_pre_ping": True}
if is_sqlite:
    # FastAPI runs sync endpoints in a threadpool; SQLite connections must be shareable.
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_recycle": 1800,
            "pool_timeout": 30,
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

if is_sqlite:

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_sqlite_schema() -> None:
    """Create all tables directly on SQLite (Alembic migrations target PostgreSQL)."""
    import app.models  # noqa: F401  (register every model on Base.metadata)
    from app.models.base import Base

    Base.metadata.create_all(bind=engine)
