import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl


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
