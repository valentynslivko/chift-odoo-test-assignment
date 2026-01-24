from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OdooContact
from src.repositories.base import CRUDBase


class OdooContactRepository(CRUDBase[OdooContact]):
    def __init__(self):
        super().__init__(OdooContact)

    async def get_contacts(
        self, db: AsyncSession, is_company: bool = False, limit: int = 100
    ) -> list[OdooContact]:
        return await self.get_multi_by_filters(db, is_company=is_company, limit=limit)


odoo_contact_repository = OdooContactRepository()
