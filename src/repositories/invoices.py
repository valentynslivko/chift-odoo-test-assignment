from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OdooInvoice
from src.repositories.base import CRUDBase


class OdooInvoiceRepository(CRUDBase[OdooInvoice]):
    def __init__(self):
        super().__init__(OdooInvoice)

    async def get_invoices(
        self, db: AsyncSession, limit: int = 100, offset: int = 0
    ) -> list[OdooInvoice]:
        return await self.get_multi_by_filters(db=db, limit=limit, offset=offset)

    async def count_invoices(self, db: AsyncSession) -> int:
        return await self.count_with_filters(db=db)

    async def get_by_odoo_id(
        self, db: AsyncSession, odoo_invoice_id: int
    ) -> OdooInvoice:
        return await self.get_by_filters(db=db, odoo_id=odoo_invoice_id)


odoo_invoice_repository = OdooInvoiceRepository()
