from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.access_grants.access_grant import AccessGrant
from domain.admins.admin_user import AdminUser
from domain.clients.client import Client
from domain.operations.operation import Operation
from domain.shared.entity_id import EntityId
from domain.shared.validation import normalize_required_text
from domain.subscriptions.subscription import Subscription
from infrastructure.db.mappers import (
    access_grant_from_row,
    access_grant_to_row,
    admin_user_from_row,
    admin_user_to_row,
    client_from_row,
    client_to_row,
    operation_from_row,
    operation_to_row,
    subscription_from_row,
    subscription_to_row,
)
from infrastructure.db.models import AccessGrantRow, AdminUserRow, ClientRow, OperationRow, SubscriptionRow


class SqlAlchemyRepository[DomainEntity, Row]:
    def __init__(
        self,
        session: Session,
        row_type: type[Row],
        to_row: Callable[[DomainEntity], Row],
        from_row: Callable[[Row], DomainEntity],
    ) -> None:
        self._session = session
        self._row_type = row_type
        self._to_row = to_row
        self._from_row = from_row

    def add(self, entity: DomainEntity) -> None:
        self._session.merge(self._to_row(entity))

    def get(self, entity_id: EntityId) -> DomainEntity | None:
        row = self._session.get(self._row_type, str(entity_id))
        if row is None:
            return None

        return self._from_row(row)


class SqlAlchemyClientRepository(SqlAlchemyRepository[Client, ClientRow]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ClientRow, client_to_row, client_from_row)


class SqlAlchemyAdminUserRepository(SqlAlchemyRepository[AdminUser, AdminUserRow]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AdminUserRow, admin_user_to_row, admin_user_from_row)

    def get_by_login(self, login: str) -> AdminUser | None:
        normalized_login = normalize_required_text(login, "login")
        row = self._session.scalar(select(self._row_type).where(self._row_type.login == normalized_login))
        if row is None:
            return None

        return self._from_row(row)


class SqlAlchemySubscriptionRepository(SqlAlchemyRepository[Subscription, SubscriptionRow]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SubscriptionRow, subscription_to_row, subscription_from_row)


class SqlAlchemyAccessGrantRepository(SqlAlchemyRepository[AccessGrant, AccessGrantRow]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AccessGrantRow, access_grant_to_row, access_grant_from_row)


class SqlAlchemyOperationRepository(SqlAlchemyRepository[Operation, OperationRow]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OperationRow, operation_to_row, operation_from_row)
