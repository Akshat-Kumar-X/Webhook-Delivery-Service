import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional

class SubscriptionCreate(BaseModel):
    target_url: HttpUrl
    secret: str | None = None
    event_types: list[str] | None = None


class SubscriptionRead(BaseModel):
    id: uuid.UUID
    target_url: HttpUrl
    secret: str | None
    event_types: list[str] | None
    created_at: datetime

    class Config:
        from_attributes = True   # v2‑style

class DeliveryAttemptRead(BaseModel):
    id: int
    status_code: Optional[int]
    success: bool
    response_ms: Optional[int]
    error: Optional[str]
    attempted_at: datetime

    class Config:
        from_attributes = True


class WebhookRequestRead(BaseModel):
    id: uuid.UUID
    payload: dict
    received_at: datetime
    attempts: list[DeliveryAttemptRead]

    class Config:
        from_attributes = True