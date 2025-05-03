import httpx, time, uuid, json, os
from datetime import datetime, timedelta

from celery import shared_task
from celery.schedules import crontab
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import models
from app.celery_app import celery
from app.cache import get_subscription  # ✅ Import the caching function


@celery.task(
    bind=True,
    autoretry_for=(Exception,),  # catch all exceptions including RuntimeError
    retry_backoff=True,
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=5,
)
def deliver_webhook(self, request_id: str):
    """Fetch payload from DB, POST to subscriber, log attempt."""
    db: Session = SessionLocal()
    req: models.WebhookRequest = db.get(models.WebhookRequest, uuid.UUID(request_id))
    if not req:
        raise self.retry(exc=RuntimeError("Request row missing"))

    # ✅ Use cached subscription
    sub_data = get_subscription(req.subscription_id)
    if not sub_data:
        raise self.retry(exc=RuntimeError("Subscription missing"))

    target_url = sub_data["target_url"]
    secret = sub_data["secret"]

    start = time.perf_counter()
    try:
        r = httpx.post(target_url, json=req.payload, timeout=10.0)
        success = r.status_code < 400
        status_code = r.status_code
        err_msg = None
    except Exception as exc:
        success = False
        status_code = None
        err_msg = str(exc)
    duration = int((time.perf_counter() - start) * 1000)

    attempt = models.DeliveryAttempt(
        request_id=req.id,
        status_code=status_code,
        success=success,
        response_ms=duration,
        error=err_msg,
    )
    db.add(attempt)
    db.commit()

    if not success:
        raise self.retry(exc=RuntimeError(f"Non-2xx status {status_code}"))

    return {"attempt_id": attempt.id, "success": success}


# Retention config
RETAIN_HOURS = int(os.getenv("ATTEMPT_RETENTION_HOURS", 72))

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every day at 02:30 UTC (≈ 08:00 IST)
    sender.add_periodic_task(
        crontab(minute=30, hour=2),
        purge_old_attempts.s(RETAIN_HOURS)
    )


@shared_task
def purge_old_attempts(retain_hours: int = 72):
    """Delete delivery_attempts older than `retain_hours`."""
    cutoff = datetime.utcnow() - timedelta(hours=retain_hours)
    db: Session = SessionLocal()
    deleted = db.query(models.DeliveryAttempt)\
        .filter(models.DeliveryAttempt.attempted_at < cutoff)\
        .delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}
