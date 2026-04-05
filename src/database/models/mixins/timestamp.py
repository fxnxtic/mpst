from datetime import datetime
from typing import Any, Final

from sqlalchemy import TIMESTAMP, Function, func
from sqlalchemy.orm import Mapped, mapped_column

NowFn: Final[Function[Any]] = func.timezone("UTC", func.now())

__all__ = ("TimestampMixin",)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=NowFn,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=NowFn,
        onupdate=NowFn,
        nullable=False,
    )
