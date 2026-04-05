from pydantic import BaseModel, Field


class LimitOffset(BaseModel):
    """Limit/offset pagination parameters. Used in BaseDAO.get_many()."""

    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @property
    def page(self) -> int:
        return self.offset // self.limit + 1
