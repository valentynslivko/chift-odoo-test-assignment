from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.db.annotations import (
    indexed_nullable_string_256,
    nullable_json_array_column,
    nullable_string_256,
    uuid_pk,
)
from src.db.base import Base
from src.db.mixins import DateTimeMixin


class User(Base, DateTimeMixin):
    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    username: Mapped[str] = mapped_column(index=True)
    hashed_password: Mapped[str]


class OdooContact(Base, DateTimeMixin):
    id: Mapped[uuid_pk]
    odoo_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[indexed_nullable_string_256]
    email: Mapped[indexed_nullable_string_256]
    company_name: Mapped[indexed_nullable_string_256]
    company_id: Mapped[nullable_json_array_column]
    is_company: Mapped[bool] = mapped_column(default=False)


class OdooInvoice(Base, DateTimeMixin):
    id: Mapped[uuid_pk]
    odoo_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[indexed_nullable_string_256]
    partner_id: Mapped[nullable_json_array_column]
    invoice_date: Mapped[nullable_string_256]  # odoo returns "YYYY-MM-DD"
    amount_total: Mapped[Optional[float]] = mapped_column(nullable=True)
    state: Mapped[nullable_string_256]
    move_type: Mapped[nullable_string_256]
