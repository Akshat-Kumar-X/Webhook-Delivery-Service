from celery import Celery
import os

# ✅ Use environment variables only, without Docker-style fallbacks
REDIS_URL = os.getenv("REDIS_URL")  # Provided by Render
BACKEND_URL = os.getenv("REDIS_BACKEND_URL", REDIS_URL)  # Optional override

# 🔧 Instantiate Celery with proper settings
celery = Celery(
    "webhook_service",
    broker=REDIS_URL,
    backend=BACKEND_URL,
    include=["app.tasks"],
)

celery.conf.update(
    task_routes={"app.tasks.*": {"queue": "deliver"}},
    task_default_retry_delay=10,  # seconds
)
