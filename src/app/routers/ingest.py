import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import models, schemas, signing
from app.db import get_session
from app.tasks import deliver_webhook

router = APIRouter(prefix="/ingest", tags=["ingest"])


class PayloadIn(schemas.BaseModel):
    subscription_id: uuid.UUID
    event_type: str
    body: dict


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def ingest(request: Request, db: Session = Depends(get_session)):
    raw = await request.body()
    try:
        payload = PayloadIn.model_validate_json(raw)
    except Exception:
        raise HTTPException(400, "Invalid JSON payload")

    sub = db.get(models.Subscription, payload.subscription_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")

    # 🔒 HMAC Signature Verification
    if sub.secret:
        header_sig = request.headers.get(signing.HEADER)
        if not header_sig or not signing.compare(signing.sign(sub.secret, raw), header_sig):
            raise HTTPException(401, "Invalid signature")

    # 🎯 Event-type filtering
    if sub.event_types and payload.event_type not in sub.event_types:
        raise HTTPException(status.HTTP_204_NO_CONTENT, "event ignored")

    req = models.WebhookRequest(subscription_id=sub.id, payload=payload.body)
    db.add(req)
    db.commit()
    db.refresh(req)

    deliver_webhook.delay(str(req.id))
    return {"request_id": req.id}
