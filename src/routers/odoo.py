from fastapi import APIRouter

from src.db.session import AsyncDBSession
from src.repositories.contacts import odoo_contact_repository
from src.services.odoo import OdooServiceDep

router = APIRouter()


@router.get("/test")
async def test(odoo_service: OdooServiceDep):
    return odoo_service.get_contacts_from_odoo()


@router.post("/create-contact", include_in_schema=False)
async def create_contact(
    odoo_service: OdooServiceDep, name: str, email: str, company_name: str
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
    return odoo_service.create_contact(name, email, company_name)


@router.get("/get-contacts")
async def get_contacts(
    db: AsyncDBSession,
    is_company: bool = False,
    limit: int = 100,
):
    return await odoo_contact_repository.get_contacts(
        db=db, is_company=is_company, limit=limit
    )
