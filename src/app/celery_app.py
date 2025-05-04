from celery import Celery
import os

BROKER_URL = os.environ["REDIS_URL"]  

# 🔧 Instantiate Celery with proper settings
celery = Celery(
    "webhook_service",
    broker=BROKER_URL,
    include=["app.tasks"],
)

celery.conf.update(
    task_ignore_result=True,         # don’t store / poll results
    task_routes={"app.tasks.*": {"queue": "deliver"}},
    task_default_retry_delay=10,
)
