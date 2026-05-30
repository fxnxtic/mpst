from typing import ClassVar
from uuid import UUID

from pydantic import Field

from src.config import cfg
from src.core.publisher import DomainEvent

DOMAIN_SUBJECT = f"{cfg.app.name}.users"


class UserCreatedMessage(DomainEvent):
    subject: ClassVar[str] = DOMAIN_SUBJECT + ".created"
    user_id: UUID = Field()
