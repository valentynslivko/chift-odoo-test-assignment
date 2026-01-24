from fastapi import APIRouter

from src.core.auth.dependencies import CurrentUserDep
from src.db.session import AsyncDBSession
from src.pagination.pagination import paginate_raw
from src.repositories.invoices import odoo_invoice_repository

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("")
async def get_invoices(
    db: AsyncDBSession,
    user: CurrentUserDep,
    page: int = 1,
    per_page: int = 100,
):
    invoices = await odoo_invoice_repository.get_invoices(
        db=db, limit=per_page, offset=(page - 1) * per_page
    )
    total_count = await odoo_invoice_repository.count_invoices(db=db)
    return paginate_raw(
        items=invoices, page=page, per_page=per_page, total_count=total_count
    )


@router.get("/{invoice_id}")
async def get_invoice(
    db: AsyncDBSession,
    user: CurrentUserDep,
    invoice_id: int,
):
    return await odoo_invoice_repository.get_by_odoo_id(
        db=db, odoo_invoice_id=invoice_id
    )
