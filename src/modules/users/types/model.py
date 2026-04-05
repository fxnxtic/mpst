from src.database.models import ModelBase
from src.database.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class UserModel(ModelBase, SoftDeleteMixin, TimestampMixin, UUIDMixin):
    __tablename__ = "user"
