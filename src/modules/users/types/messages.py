from typing import ClassVar
from uuid import UUID

from src.core.publisher import DomainEvent


class UserCreatedMessage(DomainEvent):
    subject: ClassVar[str] = "service.user.created"
    user_id: UUID
