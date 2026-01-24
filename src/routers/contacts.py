from fastapi import APIRouter

from src.core.auth.dependencies import CurrentUserDep
from src.db.session import AsyncDBSession
from src.pagination.pagination import paginate_raw
from src.repositories.contacts import odoo_contact_repository

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("")
async def get_contacts(
    db: AsyncDBSession,
    user: CurrentUserDep,
    is_company: bool = False,
    page: int = 1,
    per_page: int = 100,
):
    contacts = await odoo_contact_repository.get_contacts(
        db=db, is_company=is_company, limit=per_page, offset=(page - 1) * per_page
    )
    total_count = await odoo_contact_repository.count_contacts(
        db=db, is_company=is_company
    )
    return paginate_raw(
        items=contacts, page=page, per_page=per_page, total_count=total_count
    )


@router.get("/{contact_id}")
async def get_contact(
    db: AsyncDBSession,
    user: CurrentUserDep,
    odoo_contact_id: int,
):
    return await odoo_contact_repository.get_by_odoo_id(
        db=db, odoo_contact_id=odoo_contact_id
    )
