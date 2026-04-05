from sqlalchemy.orm import DeclarativeBase

__all__ = ("ModelBase",)


class ModelBase(DeclarativeBase):
    __abstract__ = True
