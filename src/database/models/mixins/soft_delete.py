from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ("SoftDeleteMixin",)


class SoftDeleteMixin:
    deleted: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
        nullable=False,
    )
