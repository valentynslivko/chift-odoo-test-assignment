from typing import Optional

from pydantic import BaseModel


class OdooContactCreate(BaseModel):
    odoo_id: int
    name: str
    email: str
    company_name: str
    company_id: Optional[list[int | str | dict] | bool] = None


class OdooContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[list[int | str | dict] | bool] = None


class OdooInvoiceCreate(BaseModel):
    odoo_id: int
    name: Optional[str] = None
    partner_id: Optional[list[int | str | dict] | bool] = None
    invoice_date: Optional[str] = None
    amount_total: Optional[float] = None
    state: Optional[str] = None
    move_type: Optional[str] = None


class OdooInvoiceUpdate(BaseModel):
    name: Optional[str] = None
    partner_id: Optional[list[int | str | dict] | bool] = None
    invoice_date: Optional[str] = None
    amount_total: Optional[float] = None
    state: Optional[str] = None
    move_type: Optional[str] = None
