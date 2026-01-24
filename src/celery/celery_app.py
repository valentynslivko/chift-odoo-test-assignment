from celery import Celery
from src.core.settings import get_settings

# backend dedicated celery app
settings = get_settings()

celery_app = Celery(
    "worker",
    broker=settings.REDIS_BROKER_URI,
    backend=settings.REDIS_BACKEND_URI,
    include=["src.celery.tasks"],
)

celery_app.conf.beat_schedule = {
    "sync-odoo-contacts-periodic": {
        "task": "sync_odoo_contacts",
        "schedule": settings.CELERY_BEAT_TASK_INTERVAL,
    },
    "sync-odoo-invoices-periodic": {
        "task": "sync_odoo_invoices",
        "schedule": settings.CELERY_BEAT_TASK_INTERVAL,
    },
}
celery_app.conf.timezone = "UTC"
celery_app.autodiscover_tasks()

celery_app.conf.worker_hijack_root_logger = False
