from app_layer.exceptions import AppLayerError


class AdminUserNotFoundError(AppLayerError):
    """Raised when an admin user cannot be found or is disabled."""


class AdminUserIncorrectPasswordError(AppLayerError):
    """Raised when the provided admin password does not match."""
