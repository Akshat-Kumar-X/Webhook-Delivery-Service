import uuid
from datetime import datetime      # ⬅️  NEW
from sqlalchemy import (
    String, DateTime, Boolean, JSON, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str | None] = mapped_column(String, nullable=True)
    event_types: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(            # ⬅️  FIX
        DateTime(timezone=True), server_default=func.now()
    )

    requests: Mapped[list["WebhookRequest"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


class WebhookRequest(Base):
    __tablename__ = "webhook_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(           # ⬅️  FIX
        DateTime(timezone=True), server_default=func.now()
    )

    subscription: Mapped["Subscription"] = relationship(back_populates="requests")
    attempts: Mapped[list["DeliveryAttempt"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhook_requests.id", ondelete="CASCADE"),
    )
    status_code: Mapped[int | None]
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    response_ms: Mapped[int | None]
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(          # ⬅️  FIX
        DateTime(timezone=True), server_default=func.now()
    )

    request: Mapped["WebhookRequest"] = relationship(back_populates="attempts")
