class ApplicationError(Exception):
    """Base class for application-layer failures."""


class IdempotencyConflictError(ApplicationError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Request with Idempotency-Key '{key}' has already been processed")
