import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_session

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=schemas.SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: schemas.SubscriptionCreate,
    db: Session = Depends(get_session),
):
    data = payload.model_dump(exclude_none=True)
    data["target_url"] = str(data["target_url"])
    sub = models.Subscription(**data)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/{sub_id}", response_model=schemas.SubscriptionRead)
def get_subscription(sub_id: uuid.UUID, db: Session = Depends(get_session)):
    sub = db.get(models.Subscription, sub_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")
    return sub


@router.get("", response_model=list[schemas.SubscriptionRead])
def list_subscriptions(db: Session = Depends(get_session)):
    return db.query(models.Subscription).order_by(models.Subscription.created_at.desc()).all()
