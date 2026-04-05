from typing import Any


class AppError(Exception):
    """Base exception for all application errors."""

    message: str = "An unexpected error occurred"
    status_code: int = 500

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""

    status_code = 404

    def __init__(self, entity: str | type, pk: Any) -> None:
        name = entity if isinstance(entity, str) else entity.__name__
        super().__init__(f"{name} with id={pk!r} not found")


class ConflictError(AppError):
    """Raised when an operation violates a uniqueness or state constraint."""

    status_code = 409


class ValidationError(AppError):
    """Raised when input data fails domain-level validation."""

    status_code = 422


class UnauthorizedError(AppError):
    """Raised when the caller lacks permission to perform an action."""

    status_code = 401
