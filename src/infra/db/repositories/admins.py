from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.admins.admin_user import AdminUser
from infra.db.models import AdminUserOrm
from infra.db.repositories.base import SqlAlchemyRepository, entity_id, utc, utc_or_none


class SqlAlchemyAdminUserRepository(SqlAlchemyRepository[AdminUser, AdminUserOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AdminUserOrm, self._to_orm, self._from_orm)

    def get_by_login(self, login: str) -> AdminUser | None:
        normalized_login = login.strip()
        if not normalized_login:
            return None

        orm = self._session.scalar(select(self._orm_type).where(self._orm_type.login == normalized_login))
        if orm is None:
            return None

        return self._from_orm(orm)

    @staticmethod
    def _to_orm(admin_user: AdminUser) -> AdminUserOrm:
        return AdminUserOrm(
            id=str(admin_user.id),
            login=admin_user.login,
            password_hash=admin_user.password_hash,
            last_login_at=admin_user.last_login_at,
            disabled_at=admin_user.disabled_at,
            created_at=admin_user.created_at,
        )

    @staticmethod
    def _from_orm(orm: AdminUserOrm) -> AdminUser:
        return AdminUser(
            id=entity_id(orm.id),
            login=orm.login,
            password_hash=orm.password_hash,
            last_login_at=utc_or_none(orm.last_login_at),
            disabled_at=utc_or_none(orm.disabled_at),
            created_at=utc(orm.created_at),
        )
