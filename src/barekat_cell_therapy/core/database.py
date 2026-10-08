"""Database connection."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from barekat_cell_therapy.core.config import get_settings

settings = get_settings()

_is_sqlite = settings.database_url.startswith("sqlite")
_engine_kwargs: dict = {"pool_pre_ping": True, "echo": settings.debug}
if _is_sqlite:
    # sqlite is used for hermetic integration/validation runs (no Postgres needed)
    _engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
else:
    _engine_kwargs.update(pool_size=10, max_overflow=20)

engine = create_engine(settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
