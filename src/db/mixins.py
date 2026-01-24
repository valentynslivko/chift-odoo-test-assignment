from sqlalchemy.orm import Mapped

from src.db.annotations import created_at, updated_at


class DateTimeMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
