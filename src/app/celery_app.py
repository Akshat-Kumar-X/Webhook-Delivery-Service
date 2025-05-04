# src/app/celery_app.py
from celery import Celery
import os, sys

BROKER_URL = os.environ.get("REDIS_URL")
if not BROKER_URL:
    sys.exit("❌  REDIS_URL env var missing")

celery = Celery("webhook_service", broker=BROKER_URL, include=["app.tasks"])

celery.conf.update(
    task_ignore_result=True,                 # ✅  disables result‑backend
    task_routes={"app.tasks.*": {"queue": "deliver"}},
    task_default_retry_delay=10,
)
