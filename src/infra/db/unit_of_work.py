from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from domain.operations.outbox import OutboxMessage
from domain.shared.entity import Entity
from domain.shared.time import utc_now
from infra.db.repositories import (
    SqlAlchemyAccessGrantRepository,
    SqlAlchemyAdminUserRepository,
    SqlAlchemyAuditRecordRepository,
    SqlAlchemyClientRepository,
    SqlAlchemyOperationRepository,
    SqlAlchemyOutboxMessageRepository,
    SqlAlchemySubscriptionRepository,
    SqlAlchemySubscriptionRevisionRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self._session_factory()
        self._tracked: set[Entity] = set()
        self.admins = SqlAlchemyAdminUserRepository(self.session)
        self.clients = SqlAlchemyClientRepository(self.session)
        self.subscriptions = SqlAlchemySubscriptionRepository(self.session)
        self.access_grants = SqlAlchemyAccessGrantRepository(self.session)
        self.operations = SqlAlchemyOperationRepository(self.session)
        self.subscription_revisions = SqlAlchemySubscriptionRevisionRepository(self.session)
        self.audit_records = SqlAlchemyAuditRecordRepository(self.session)
        self.outbox_messages = SqlAlchemyOutboxMessageRepository(self.session)
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

    def track(self, entity: Entity) -> None:
        self._tracked.add(entity)

    def commit(self) -> None:
        self._dispatch_outbox()
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def shutdown(self) -> None:
        self.session.close()

    def _dispatch_outbox(self) -> None:
        now = utc_now()
        for entity in self._tracked:
            for event in entity.pull_domain_events():
                message = OutboxMessage(
                    event_type=type(event).__name__,
                    payload=event.model_dump(mode="json"),
                    created_at=now,
                )
                self.outbox_messages.add(message)
