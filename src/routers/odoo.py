from fastapi import APIRouter

from src.core.auth.dependencies import CurrentUserDep
from src.db.session import AsyncDBSession
from src.repositories.contacts import odoo_contact_repository
from src.services.odoo import OdooServiceDep

router = APIRouter(prefix="/api/odoo", tags=["odoo"])


@router.get("/get-contacts-from-odoo")
async def get_contacts_from_odoo(
    user: CurrentUserDep, odoo_service: OdooServiceDep, limit: int = 100
):
    return odoo_service.get_contacts_from_odoo(limit=limit)


@router.post("/create-contact")
# TODO: include_in_schema=False
async def create_contact(
    user: CurrentUserDep,
    odoo_service: OdooServiceDep,
    db: AsyncDBSession,
    name: str,
    email: str,
    company_name: str,
):
    """
    Helper endpoint to create a contact in Odoo for tests during the development.
    Args:
        name: str
        email: str
        company_name: str

    Returns:
        int: Odoo contact ID
    """
    return await odoo_service.create_and_insert_contact(db, name, email, company_name)


@router.get("/get-contacts")
async def get_contacts(
    db: AsyncDBSession,
    user: CurrentUserDep,
    is_company: bool = False,
    limit: int = 100,
):
    return await odoo_contact_repository.get_contacts(
        db=db, is_company=is_company, limit=limit
    )
