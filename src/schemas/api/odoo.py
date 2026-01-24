from pydantic import BaseModel


class InvoiceCreatePayload(BaseModel):
    name: str
    quantity: int
    price_unit: float
