from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from domain.admins.admin_user import AdminUser
from infrastructure.db import (
    AdminUserRow,
    Base,
    admin_user_from_row,
    admin_user_to_row,
    create_session_factory,
    create_sqlite_engine,
)
from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def test_admin_user_round_trip_mapping(tmp_path: Path) -> None:
    admin_user = AdminUser(
        id=UUID("00000000-0000-0000-0000-000000000101"),
        login="root",
        password_hash="hash-123",
        last_login_at=datetime(2026, 6, 15, 10, 0, 0, tzinfo=UTC),
        disabled_at=datetime(2026, 6, 15, 11, 0, 0, tzinfo=UTC),
        created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
    )

    loaded_admin_user = _persist_round_trip(
        tmp_path,
        admin_user_to_row(admin_user),
        AdminUserRow,
        admin_user_from_row,
    )

    assert asdict(loaded_admin_user) == asdict(admin_user)


def test_admin_user_repository_looks_up_by_login(tmp_path: Path) -> None:
    admin_user = AdminUser(login="root", password_hash="hash-123")
    session_factory = _session_factory(tmp_path)

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.admins.add(admin_user)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        loaded_admin_user = unit_of_work.admins.get_by_login("root")

    assert loaded_admin_user is not None
    assert asdict(loaded_admin_user) == asdict(admin_user)


def _persist_round_trip(
    tmp_path: Path,
    row: object,
    row_type: type[object],
    from_row: Callable[[object], object],
) -> object:
    database_path = tmp_path / "admin-users.db"
    engine = create_sqlite_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(row)
        session.commit()

    with session_factory() as session:
        loaded_row = session.get(row_type, row.id)
        assert loaded_row is not None

    try:
        return from_row(loaded_row)
    finally:
        engine.dispose()


def _session_factory(tmp_path: Path):
    engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'uow-admin.db'}")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)
