from pathlib import Path

from infra.db.sqlite import SQLITE_BUSY_TIMEOUT_MS, create_sqlite_engine


def test_sqlite_engine_applies_pragmas(tmp_path: Path) -> None:
    database_path = tmp_path / "persistence.db"
    engine = create_sqlite_engine(f"sqlite:///{database_path}")

    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
        assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one().lower() == "wal"
        assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == SQLITE_BUSY_TIMEOUT_MS
