import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_persistence_tables(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    table_names = set(inspect(engine).get_table_names())
    engine.dispose()

    assert {
        "admin_users",
        "access_grants",
        "alembic_version",
        "clients",
        "operations",
        "subscriptions",
    }.issubset(table_names)


def test_alembic_config_works_without_pytest_pythonpath(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'subprocess-migrations.db'}"
    script = (
        "from alembic import command\n"
        "from alembic.config import Config\n"
        "config = Config('alembic.ini')\n"
        f"config.set_main_option('sqlalchemy.url', {database_url!r})\n"
        "command.upgrade(config, 'head')\n"
    )

    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
