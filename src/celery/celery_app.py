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

# celery_app.conf.beat_schedule = {
#     "run-periodic-task": {
#         # schedule expects seconds
#         "schedule": 60,  # TODO: settings
#     },
# }
celery_app.conf.timezone = "UTC"
celery_app.autodiscover_tasks()

celery_app.conf.worker_hijack_root_logger = False
