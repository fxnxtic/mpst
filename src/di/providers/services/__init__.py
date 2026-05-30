from .users import UserServiceProvider

__all__ = (
    "UserServiceProvider",
    "SERVICE_PROVIDERS",
)

SERVICE_PROVIDERS = [UserServiceProvider()]
