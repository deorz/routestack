from collections.abc import Iterable
from enum import Enum
from typing import Any

from domain.shared.errors import DomainValidationError


def ensure_type(value: object, expected_type: type[Any], field_name: str) -> Any:
    if not isinstance(value, expected_type):
        raise DomainValidationError(f"{field_name} must be a {expected_type.__name__}")

    return value


def ensure_enum(value: object, enum_type: type[Enum], field_name: str) -> Enum:
    if not isinstance(value, enum_type):
        raise DomainValidationError(f"{field_name} must be a {enum_type.__name__}")

    return value


def normalize_required_text(value: str, field_name: str) -> str:
    normalized = ensure_type(value, str, field_name).strip()
    if not normalized:
        raise DomainValidationError(f"{field_name} cannot be blank")

    return normalized


def normalize_optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None

    normalized = normalize_required_text(value, field_name)
    return normalized


def normalize_tags(values: Iterable[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()

    tags: list[str] = []
    for value in values:
        tags.append(normalize_required_text(value, "tags entry"))
    return tuple(tags)


def ensure_non_negative_int(value: int, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise DomainValidationError(f"{field_name} must be an integer")

    if value < 0:
        raise DomainValidationError(f"{field_name} cannot be negative")

    return value


def ensure_positive_int(value: int, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise DomainValidationError(f"{field_name} must be an integer")

    if value < 1:
        raise DomainValidationError(f"{field_name} must be positive")

    return value

