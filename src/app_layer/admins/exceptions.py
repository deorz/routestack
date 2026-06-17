from app_layer.exceptions import ApplicationError


class AdminUserNotFoundError(ApplicationError):
    """Raised when an admin user cannot be found or is disabled."""


class AdminUserIncorrectPasswordError(ApplicationError):
    """Raised when the provided admin password does not match."""
