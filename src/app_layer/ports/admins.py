from typing import Protocol, runtime_checkable

from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import EntityId


@runtime_checkable
class AdminAuthenticationService(Protocol):
    def bootstrap_user(self, *, login: str, password: str) -> AdminUser: ...

    def authenticate(self, *, login: str, password: str) -> AdminUser: ...

    def get_enabled_user(self, admin_user_id: EntityId) -> AdminUser: ...
