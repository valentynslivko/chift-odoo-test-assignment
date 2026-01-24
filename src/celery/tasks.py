import asyncio
import logging

from src.celery.celery_app import celery_app
from src.db.session import async_session
from src.repositories.contacts import odoo_contact_repository
from src.repositories.invoices import odoo_invoice_repository
from src.schemas.odoo.schemas import (
    OdooContactCreate,
    OdooContactUpdate,
    OdooInvoiceCreate,
    OdooInvoiceUpdate,
)
from src.services.odoo import OdooService

logger = logging.getLogger(__name__)


@celery_app.task(name="sync_odoo_contacts")
def sync_odoo_contacts():
    """
    Celery beat task to sync contacts from Odoo to local database.
    """

    async def _sync():
        service = OdooService()
        try:
            # NOTE: pagination traversal depends on the business logic, skipping it in the assignment
            contacts = service.get_contacts_from_odoo(limit=100)
            logger.info(f"fetched {len(contacts)} contacts from odoo")

            async with async_session() as db:
                for contact in contacts:
                    odoo_id = contact.get("id")
                    if not odoo_id:
                        continue

                    # prepare contact data
                    # odoo company_id is usually [id, name] or False
                    company_id_raw = contact.get("company_id")
                    company_name = ""
                    if isinstance(company_id_raw, list) and len(company_id_raw) > 1:
                        company_name = company_id_raw[1]

                    contact_data = {
                        "odoo_id": odoo_id,
                        "name": contact.get("name") or "",
                        "email": contact.get("email") or "",
                        "company_name": company_name,
                        "company_id": company_id_raw,
                    }

                    existing_contact = await odoo_contact_repository.get_by_filters(
                        db, odoo_id=odoo_id
                    )

                    if existing_contact:
                        # update existing contact
                        obj_in = OdooContactUpdate(**contact_data)
                        await odoo_contact_repository.update(
                            db, db_obj=existing_contact, obj_in=obj_in
                        )
                    else:
                        # create new contact
                        obj_in = OdooContactCreate(**contact_data)
                        await service.insert_contact(db, obj_in=obj_in)

                await db.commit()
                logger.info("successfully synced odoo contacts to database")

        except Exception as e:
            logger.error(f"failed to sync odoo contacts: {str(e)}")
            raise e

    asyncio.run(_sync())


@celery_app.task(name="sync_odoo_invoices")
def sync_odoo_invoices():
    """
    Celery beat task to sync invoices from Odoo to local database.
    """

    async def _sync():
        service = OdooService()
        try:
            # NOTE: pagination traversal depends on the business logic, skipping it in the assignment
            invoices = service.get_invoices_from_odoo(limit=100)
            logger.info(f"fetched {len(invoices)} invoices from odoo")

            async with async_session() as db:
                for invoice in invoices:
                    odoo_id = invoice.get("id")
                    if not odoo_id:
                        continue

                    invoice_data = {
                        "odoo_id": odoo_id,
                        "name": invoice.get("name"),
                        "partner_id": invoice.get("partner_id"),
                        "invoice_date": invoice.get("invoice_date"),
                        "amount_total": invoice.get("amount_total"),
                        "state": invoice.get("state"),
                        "move_type": invoice.get("move_type"),
                    }

                    existing_invoice = await odoo_invoice_repository.get_by_filters(
                        db, odoo_id=odoo_id
                    )

                    if existing_invoice:
                        obj_in = OdooInvoiceUpdate(**invoice_data)
                        await odoo_invoice_repository.update(
                            db, db_obj=existing_invoice, obj_in=obj_in
                        )
                    else:
                        obj_in = OdooInvoiceCreate(**invoice_data)
                        await service.insert_invoice(db, obj_in=obj_in)

                await db.commit()
                logger.info("successfully synced odoo invoices to database")

        except Exception as e:
            logger.error(f"failed to sync odoo invoices: {str(e)}")
            raise e

    asyncio.run(_sync())
