from typing import Protocol

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session, sessionmaker


class DbApiCursor(Protocol):
    def execute(self, statement: str) -> object: ...

    def close(self) -> None: ...


class DbApiConnection(Protocol):
    def cursor(self) -> DbApiCursor: ...


SQLITE_BUSY_TIMEOUT_MS = 5_000


def create_sqlite_engine(
    url: str | URL,
    *,
    echo: bool = False,
    busy_timeout_ms: int = SQLITE_BUSY_TIMEOUT_MS,
) -> Engine:
    engine = create_engine(url, echo=echo)

    @event.listens_for(engine, "connect")
    def _configure_sqlite_connection(dbapi_connection: DbApiConnection, connection_record: object) -> None:
        del connection_record

        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")
        finally:
            cursor.close()

    return engine


def create_session_factory(
    engine: Engine,
    *,
    expire_on_commit: bool = False,
) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=expire_on_commit)
