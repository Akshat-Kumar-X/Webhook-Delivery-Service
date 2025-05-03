import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_session
from app.tasks import deliver_webhook

router = APIRouter(prefix="/ingest", tags=["ingest"])


class PayloadIn(schemas.BaseModel):
    subscription_id: uuid.UUID
    body: dict


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def ingest(payload: PayloadIn, db: Session = Depends(get_session)):
    sub = db.get(models.Subscription, payload.subscription_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")

    req = models.WebhookRequest(subscription_id=sub.id, payload=payload.body)
    db.add(req)
    db.commit()
    db.refresh(req)

    deliver_webhook.delay(str(req.id))  # asynchronous push to worker
    return {"request_id": req.id}
