import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

app = Celery("library_settings")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "notify-overdue-every-day": {
        "task": "borrowing.tasks.notify_overdue_borrowings",
        "schedule": crontab(hour=9, minute=0),
    },
}
