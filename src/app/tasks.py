import httpx, time, uuid, json
from celery import shared_task

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models

@shared_task(
    bind=True,
    autoretry_for=(httpx.HTTPError, ),
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
        self.retry(countdown=5, exc=RuntimeError("Request row missing"))

    sub = req.subscription
    start = time.perf_counter()
    try:
        r = httpx.post(sub.target_url, json=req.payload, timeout=10.0)
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
        raise self.retry(exc=RuntimeError("Delivery failed"), countdown=10)

    return {"attempt_id": attempt.id, "success": success}
