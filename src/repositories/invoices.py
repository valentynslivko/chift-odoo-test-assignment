from src.models import OdooInvoice
from src.repositories.base import CRUDBase


class OdooInvoiceRepository(CRUDBase[OdooInvoice]):
    def __init__(self):
        super().__init__(OdooInvoice)


odoo_invoice_repository = OdooInvoiceRepository()
