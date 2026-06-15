from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from infrastructure.db.repositories import (
    SqlAlchemyAccessGrantRepository,
    SqlAlchemyClientRepository,
    SqlAlchemyOperationRepository,
    SqlAlchemySubscriptionRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self._session_factory()
        self.clients = SqlAlchemyClientRepository(self.session)
        self.subscriptions = SqlAlchemySubscriptionRepository(self.session)
        self.access_grants = SqlAlchemyAccessGrantRepository(self.session)
        self.operations = SqlAlchemyOperationRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
