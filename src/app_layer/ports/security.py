from typing import Protocol, runtime_checkable


@runtime_checkable
class PasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...

    def verify_password(self, password: str, password_hash: str) -> bool: ...


@runtime_checkable
class AccessTokenGenerator(Protocol):
    def generate(self) -> tuple[str, str]: ...

    def verify(self, raw_token: str, hashed_token: str) -> bool: ...
