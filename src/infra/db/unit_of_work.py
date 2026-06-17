from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from infra.db.repositories import (
    SqlAlchemyAccessGrantRepository,
    SqlAlchemyAdminUserRepository,
    SqlAlchemyAuditRecordRepository,
    SqlAlchemyClientRepository,
    SqlAlchemyOperationRepository,
    SqlAlchemySubscriptionRepository,
    SqlAlchemySubscriptionRevisionRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self._session_factory()
        self.admins = SqlAlchemyAdminUserRepository(self.session)
        self.clients = SqlAlchemyClientRepository(self.session)
        self.subscriptions = SqlAlchemySubscriptionRepository(self.session)
        self.access_grants = SqlAlchemyAccessGrantRepository(self.session)
        self.operations = SqlAlchemyOperationRepository(self.session)
        self.subscription_revisions = SqlAlchemySubscriptionRevisionRepository(self.session)
        self.audit_records = SqlAlchemyAuditRecordRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
        finally:
            self.shutdown()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def shutdown(self) -> None:
        self.session.close()
