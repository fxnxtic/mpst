from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ("UUIDMixin",)


class UUIDMixin:
    id_: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
    )
