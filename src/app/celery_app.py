from celery import Celery

import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND_URL = os.getenv("REDIS_BACKEND_URL", "redis://redis:6379/1")

celery = Celery(
    "webhook_service",
    broker=REDIS_URL,
    backend=BACKEND_URL,
    include=["app.tasks"],   # auto‑discover below
)

celery.conf.update(
    task_routes={"app.tasks.*": {"queue": "deliver"}},
    task_default_retry_delay=10,  # seconds; will be overridden later
)
