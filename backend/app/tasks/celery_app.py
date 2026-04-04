from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("supergov", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Almaty",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "poll_application_statuses": {
        "task": "app.tasks.status_poller.poll_statuses",
        "schedule": 900.0, # Every 15 min
    },
    "recalc_benefits_daily": {
        "task": "app.tasks.benefits_calc.calc_all",
        "schedule": crontab(hour=3, minute=0), # 3am daily
    },
    "recalc_analytics_weekly": {
        "task": "app.tasks.analytics_calc.calc_agency_scores",
        "schedule": crontab(day_of_week='sun', hour=4, minute=0),
    }
}
