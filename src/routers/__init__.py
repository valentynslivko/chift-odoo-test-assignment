from src.routers.auth import router as auth_router
from src.routers.contacts import router as contacts_router
from src.routers.invoices import router as invoices_router
from src.routers.odoo import router as odoo_router

__all__ = (
    "auth_router",
    "contacts_router",
    "odoo_router",
    "invoices_router",
)
