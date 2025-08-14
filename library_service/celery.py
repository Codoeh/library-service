import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

app = Celery("library_settings")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()