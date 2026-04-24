from celery import Celery
from celery.schedules import crontab

from config import get_settings

settings = get_settings()

celery_app = Celery("pulse_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
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

celery_app.autodiscover_tasks(["tasks"])
