from typing import Annotated

from fastapi import Depends, HTTPException

from src.db.session import AsyncDBSession
from src.repositories.contacts import odoo_contact_repository
from src.rpc.client import OdooClient
from src.schemas.odoo.schemas import OdooContactCreate, OdooContactUpdate


class OdooService:
    def __init__(self):
        self.client = OdooClient()  # normally injected via DI

    def get_contacts_from_odoo(self, limit: int = 100) -> list[dict]:
        return self.client.get_contacts(limit=limit)

    def version(self) -> str:
        return self.client.version()

    def create_contact(self, name: str, email: str, company_name: str) -> int:
        return self.client.create_contact(name, email, company_name)

    def insert_contact(
        self, db: AsyncDBSession, name: str, email: str, company_name: str
    ):
        return odoo_contact_repository.create(
            db, OdooContactCreate(name=name, email=email, company_name=company_name)
        )

    async def update_contact(
        self, db: AsyncDBSession, contact_id: int, obj_in: OdooContactUpdate
    ):
        db_obj = await odoo_contact_repository.get(db, contact_id)
        return await odoo_contact_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_contact(self, db: AsyncDBSession, contact_id: int):
        db_obj = await odoo_contact_repository.get(db, contact_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Contact not found")
        return await odoo_contact_repository.delete(db, db_obj)


OdooServiceDep = Annotated[OdooService, Depends(OdooService)]
