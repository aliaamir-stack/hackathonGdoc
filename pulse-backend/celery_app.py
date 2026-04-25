from celery import Celery
from celery.schedules import crontab

from config import get_settings

settings = get_settings()

celery_app = Celery(
    "pulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks.outbreak_detection", "tasks.who_rss"]
)

# Fix for Upstash/Redis SSL issues
if settings.REDIS_URL.startswith("rediss://"):
    celery_app.conf.update(
        broker_use_ssl={"ssl_cert_reqs": "none"},
        redis_backend_use_ssl={"ssl_cert_reqs": "none"}
    )

celery_app.conf.update(
    result_expires=3600,
    timezone="UTC",
    beat_schedule={
        "fetch_who_rss_hourly": {
            "task": "tasks.who_rss.fetch_who_rss",
            "schedule": crontab(minute=0, hour="*"),
        },
        "run_outbreak_detection_15m": {
            "task": "tasks.outbreak_detection.run_outbreak_detection",
            "schedule": crontab(minute="*/15"),
        },
    },
)

# celery_app.autodiscover_tasks(["tasks"]) # Removed to prevent Beat import errors

