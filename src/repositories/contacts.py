from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OdooContact
from src.repositories.base import CRUDBase


class OdooContactRepository(CRUDBase[OdooContact]):
    def __init__(self):
        super().__init__(OdooContact)

    async def get_contacts(
        self,
        db: AsyncSession,
        is_company: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OdooContact]:
        return await self.get_multi_by_filters(
            db, is_company=is_company, limit=limit, offset=offset
        )

    async def get_by_odoo_id(
        self, db: AsyncSession, odoo_contact_id: int
    ) -> OdooContact:
        return await self.get_by_filters(db=db, odoo_id=odoo_contact_id)

    async def count_contacts(self, db: AsyncSession, is_company: bool = False) -> int:
        return await self.count_with_filters(db=db, is_company=is_company)


odoo_contact_repository = OdooContactRepository()
