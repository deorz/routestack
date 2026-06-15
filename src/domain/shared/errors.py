class DomainError(Exception):
    """Base class for domain-level failures."""


class DomainValidationError(DomainError, ValueError):
    """Raised when a domain value fails validation."""


class DomainStateError(DomainError, RuntimeError):
    """Raised when a lifecycle transition is not allowed."""
