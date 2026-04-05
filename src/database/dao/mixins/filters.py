from pydantic import BaseModel


class BaseFilters(BaseModel):
    """
    Base class for domain-specific filter schemas.

    Subclass and add Optional fields — BaseDAO.get_many() will
    automatically build WHERE clauses from any non-None fields
    that match a column name on the ORM model.

    Example:
        class ItemFilters(BaseFilters):
            status: ItemStatus | None = None
            owner_id: UUID | None = None
    """

    model_config = {"extra": "ignore"}

    def to_clauses(self, model: type) -> list:
        """
        Convert non-None filter fields to SQLAlchemy WHERE clauses.
        Fields that don't correspond to a model column are silently skipped.
        """
        from sqlalchemy import inspect as sa_inspect

        mapper = sa_inspect(model)
        column_names = {col.key for col in mapper.columns}

        clauses = []
        for field, value in self.model_dump(exclude_none=True).items():
            if field in column_names:
                clauses.append(getattr(model, field) == value)
        return clauses
