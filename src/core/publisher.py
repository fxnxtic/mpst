from __future__ import annotations

from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID, uuid4

from faststream.nats import NatsBroker
from opentelemetry import trace
from pydantic import BaseModel, Field

from src.core.telemetry import get_logger

__all__ = (
    "DomainEvent",
    "MessagePublisher",
)

logger = get_logger(__name__)


class DomainEvent(BaseModel):
    """
    Base class for all domain events.

    Every subclass MUST define:
        subject: ClassVar[str] = "my-service.domain.verb"

    Fields populated automatically at construction:
        event_id       — unique ID for this event instance (dedup key)
        correlation_id — trace correlation, override to propagate from request
        occurred_at    — UTC timestamp of when the event was created
    """

    model_config = {"frozen": True}

    subject: ClassVar[str]

    event_id: UUID = Field(default_factory=uuid4)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def nats_msg_id(self) -> str:
        """
        Deterministic deduplication key for NATS JetStream.
        Uses event_id so re-publishing the same event object is idempotent.
        Passed as the Nats-Msg-Id header.
        """
        return str(self.event_id)


class MessagePublisher:
    """
    Per-request/message publisher with a collect→flush lifecycle.
    """

    def __init__(self, broker: NatsBroker) -> None:  # NatsBroker
        self._broker = broker
        self._pending: list[DomainEvent] = []

    async def __aenter__(self) -> MessagePublisher: ...

    async def __aexit__(self, *args) -> None:
        self.discard()

    def collect(self, event: DomainEvent) -> None:
        """
        Buffer an event for deferred publishing.

        Call from BaseService lifecycle hooks (after_create, after_update,
        after_delete). The event will not be published until flush() is
        called — which should happen only after uow.commit() succeeds.

        Thread-safe: each REQUEST/MESSAGE scope has its own instance.
        """
        self._pending.append(event)
        logger.debug(
            "event collected",
            extra=dict(
                event_type=type(event).__name__,
                subject=event.subject,
                event_id=str(event.event_id),
                pending_count=len(self._pending),
            ),
        )

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single event immediately.

        Use from orchestrators AFTER uow.commit(). Do not call from
        service hooks — the transaction may not be committed yet.
        """
        await self._send(event)

    async def flush(self) -> int:
        """
        Publish all collected events and clear the buffer.

        Call after uow.commit() in the router or handler.
        Returns the number of events published.
        """
        if not self._pending:
            return 0

        events = list(self._pending)  # snapshot — don't mutate during iteration
        published = 0

        for event in events:
            await self._send(event)
            published += 1

        self._pending.clear()

        logger.debug("events flushed", extra=dict(count=published))
        return published

    def discard(self) -> int:
        """
        Discard all collected events without publishing.

        Call on rollback / exception path so stale events don't
        leak into the next request via a reused publisher instance.
        Returns the number of events discarded.
        """
        count = len(self._pending)
        if count:
            logger.warning(
                "events discarded",
                extra=dict(
                    count=count,
                    event_types=[type(e).__name__ for e in self._pending],
                ),
            )
        self._pending.clear()
        return count

    @property
    def pending_count(self) -> int:
        """Number of events waiting to be flushed. Useful in tests."""
        return len(self._pending)

    def pending_events(self) -> list[DomainEvent]:
        """
        Return a copy of the pending event list.
        Useful for assertions in unit tests:
            assert len(publisher.pending_events()) == 1
            assert isinstance(publisher.pending_events()[0], ItemCreatedEvent)
        """
        return list(self._pending)

    async def _send(self, event: DomainEvent) -> None:
        """
        Publish one event to NATS JetStream with dedup header and
        OTEL span attributes.
        """
        self._annotate_span(event)

        try:
            await self._broker.publish(
                event.model_dump(mode="json"),
                subject=event.subject,
                headers={"Nats-Msg-Id": event.nats_msg_id()},
            )
            logger.info(
                "event published",
                extra=dict(
                    event_type=type(event).__name__,
                    subject=event.subject,
                    event_id=str(event.event_id),
                    correlation_id=event.correlation_id,
                ),
            )
        except Exception:
            logger.error(
                "event publish failed",
                extra=dict(
                    event_type=type(event).__name__,
                    subject=event.subject,
                    event_id=str(event.event_id),
                ),
            )
            raise

    @staticmethod
    def _annotate_span(event: DomainEvent) -> None:
        """
        Add event metadata to the current OTEL span so Jaeger shows
        which events were published within a trace.
        """
        span = trace.get_current_span()
        if span.is_recording():
            span.add_event(
                f"event.publish:{type(event).__name__}",
                attributes={
                    "messaging.system": "nats",
                    "messaging.destination": event.subject,
                    "event.id": str(event.event_id),
                    "event.type": type(event).__name__,
                    "event.correlation_id": event.correlation_id,
                },
            )
