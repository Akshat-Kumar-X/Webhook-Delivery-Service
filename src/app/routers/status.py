import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.db import get_session

router = APIRouter(prefix="/status", tags=["status"])


@router.get(
    "/request/{request_id}",
    response_model=schemas.WebhookRequestRead,
)
def request_status(
    request_id: uuid.UUID,
    db: Session = Depends(get_session),
):
    req = (
        db.query(models.WebhookRequest)
        .options(joinedload(models.WebhookRequest.attempts))
        .get(request_id)
    )
    if not req:
        raise HTTPException(404, detail="Request not found")
    # Sort attempts newest‑first for convenience
    req.attempts.sort(key=lambda a: a.attempted_at, reverse=True)
    return req


@router.get(
    "/subscription/{sub_id}",
    response_model=List[schemas.DeliveryAttemptRead],
)
def subscription_recent(
    sub_id: uuid.UUID,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    q = (
        db.query(models.DeliveryAttempt)
        .join(models.WebhookRequest)
        .filter(models.WebhookRequest.subscription_id == sub_id)
        .order_by(models.DeliveryAttempt.attempted_at.desc())
        .limit(limit)
    )
    return q.all()
