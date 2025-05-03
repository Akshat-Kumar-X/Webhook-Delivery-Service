import functools, uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from app import models
from app.db import SessionLocal

TTL_SECONDS = 60


def _make_key(sub_id: uuid.UUID):
    return str(sub_id)


def _store(sub: models.Subscription):
    """Return a deep‑copy‑safe dict (so callers can mutate without side‑effects)."""
    return {
        "id": sub.id,
        "target_url": sub.target_url,
        "secret": sub.secret,
        "event_types": sub.event_types,
    }


@functools.lru_cache(maxsize=1024)
def _cached_subscription(key: str):
    """Internal function wrapped by lru_cache."""
    sub_id = uuid.UUID(key)
    db: Session = SessionLocal()
    sub = db.get(models.Subscription, sub_id)
    if not sub:
        raise KeyError(f"Subscription {sub_id} not found")
    # Inject our own expiry marker
    return _store(sub) | {"_cached_at": datetime.utcnow()}


def get_subscription(sub_id: uuid.UUID) -> Optional[dict]:
    """Public accessor with TTL invalidation."""
    key = _make_key(sub_id)
    try:
        data = _cached_subscription(key)
        if datetime.utcnow() - data["_cached_at"] > timedelta(seconds=TTL_SECONDS):
            _cached_subscription.cache_pop(key, None)  # expire
            data = _cached_subscription(key)           # refetch
        return data
    except KeyError:
        return None
