from typing import Optional

from pydantic import BaseModel


class OdooContactCreate(BaseModel):
    name: str
    email: str
    company_name: str
    company_id: list[int | str | dict] | bool


class OdooContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[list[int | str | dict] | bool] = None
