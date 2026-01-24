from fastapi import APIRouter

from src.core.auth.dependencies import CurrentUserDep
from src.db.session import AsyncDBSession
from src.repositories.contacts import odoo_contact_repository
from src.schemas.api.odoo import InvoiceCreatePayload
from src.services.odoo import OdooServiceDep

router = APIRouter(prefix="/api/utils", tags=["utils"])

# NOTE: all endpoints/interfaces from this router are for utils and testing purposes of odoo API functionality


@router.get("/odoo-contacts")
async def get_contacts_from_odoo(
    user: CurrentUserDep,
    odoo_service: OdooServiceDep,
    limit: int = 100,
    offset: int = 0,
):
    return odoo_service.get_contacts_from_odoo(limit=limit, offset=offset)


@router.post("/odoo-create-contact")
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


@router.get("/odoo-contacts")
async def get_contacts(
    db: AsyncDBSession,
    user: CurrentUserDep,
    is_company: bool = False,
    limit: int = 100,
):
    return await odoo_contact_repository.get_contacts(
        db=db, is_company=is_company, limit=limit
    )


@router.get("/odoo-invoices")
async def get_invoices_from_odoo(
    user: CurrentUserDep,
    odoo_service: OdooServiceDep,
    limit: int = 100,
    offset: int = 0,
):
    return odoo_service.get_invoices_from_odoo(limit=limit, offset=offset)


@router.post("/odoo-create-invoice")
async def create_invoice(
    user: CurrentUserDep,
    odoo_service: OdooServiceDep,
    db: AsyncDBSession,
    partner_id: int,
    invoice_lines: list[InvoiceCreatePayload],
):
    return await odoo_service.create_and_insert_invoice(
        db=db, partner_id=partner_id, invoice_lines=invoice_lines
    )


@router.get("/odoo-partners-list")
async def get_partners_from_odoo(
    user: CurrentUserDep,
    odoo_service: OdooServiceDep,
    limit: int = 100,
    offset: int = 0,
):
    return odoo_service.client.get_partners(limit=limit, offset=offset)
