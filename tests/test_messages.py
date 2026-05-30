from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.core.publisher import DomainEvent, MessagePublisher
from src.services.users.types.messages import UserCreatedMessage


class TestDomainEvent:
    def test_creates_with_defaults(self):
        event = DomainEvent()

        assert isinstance(event.event_id, UUID)
        assert isinstance(event.correlation_id, str)
        assert isinstance(event.occurred_at, datetime)
        assert event.occurred_at.tzinfo is UTC

    def test_frozen_model(self):
        event = DomainEvent()

        with pytest.raises((TypeError, ValidationError)):
            event.event_id = uuid4()

    def test_nats_msg_id(self):
        event = DomainEvent()

        assert event.nats_msg_id() == str(event.event_id)

    def test_unique_event_ids(self):
        ids = {DomainEvent().event_id for _ in range(100)}

        assert len(ids) == 100

    def test_occurred_at_set_on_creation(self):
        before = datetime.now(UTC)
        event = DomainEvent()
        after = datetime.now(UTC)

        assert before <= event.occurred_at <= after


class TestUserCreatedMessage:
    def test_subject_contains_domain(self):
        msg = UserCreatedMessage(user_id=uuid4())

        assert "users.created" in msg.subject

    def test_subject_is_classvar(self):
        assert isinstance(UserCreatedMessage.subject, str)

    def test_creates_with_user_id(self):
        user_id = uuid4()
        msg = UserCreatedMessage(user_id=user_id)

        assert msg.user_id == user_id

    def test_inherits_domain_event_behavior(self):
        msg = UserCreatedMessage(user_id=uuid4())

        assert isinstance(msg, DomainEvent)
        assert isinstance(msg.event_id, UUID)
        assert msg.nats_msg_id() == str(msg.event_id)

    def test_frozen(self):
        msg = UserCreatedMessage(user_id=uuid4())

        with pytest.raises((TypeError, ValidationError)):
            msg.user_id = uuid4()


class TestMessagePublisher:
    @pytest.fixture
    def broker(self):
        return AsyncMock()

    @pytest.fixture
    def publisher(self, broker):
        return MessagePublisher(broker=broker)

    def test_collect_adds_to_pending(self, publisher):
        event = UserCreatedMessage(user_id=uuid4())

        publisher.collect(event)

        assert publisher.pending_count == 1

    def test_pending_events_returns_copy(self, publisher):
        event = UserCreatedMessage(user_id=uuid4())

        publisher.collect(event)

        events = publisher.pending_events()
        assert len(events) == 1
        assert events[0] is event

        events.clear()

        assert publisher.pending_count == 1

    async def test_flush_publishes_and_clears(self, publisher, broker):
        event = UserCreatedMessage(user_id=uuid4())

        publisher.collect(event)
        count = await publisher.flush()

        assert count == 1
        assert publisher.pending_count == 0
        broker.publish.assert_awaited_once()

    async def test_flush_empty_returns_zero(self, publisher, broker):
        count = await publisher.flush()

        assert count == 0
        broker.publish.assert_not_awaited()

    async def test_discard_clears_without_publishing(self, publisher, broker):
        event = UserCreatedMessage(user_id=uuid4())

        publisher.collect(event)
        count = publisher.discard()

        assert count == 1
        assert publisher.pending_count == 0
        broker.publish.assert_not_awaited()

    async def test_discard_empty_returns_zero(self, publisher):
        count = publisher.discard()

        assert count == 0

    async def test_aexit_discards_pending(self, publisher, broker):
        event = UserCreatedMessage(user_id=uuid4())

        publisher.collect(event)
        async with publisher:
            pass

        assert publisher.pending_count == 0
        broker.publish.assert_not_awaited()

    async def test_flush_multiple_events(self, publisher, broker):
        events = [UserCreatedMessage(user_id=uuid4()) for _ in range(3)]

        for e in events:
            publisher.collect(e)
        count = await publisher.flush()

        assert count == 3
        assert publisher.pending_count == 0
        assert broker.publish.await_count == 3

    async def test_publish_single_event(self, publisher, broker):
        event = UserCreatedMessage(user_id=uuid4())

        await publisher.publish(event)

        broker.publish.assert_awaited_once()

    async def test_publish_uses_correct_subject(self, publisher, broker):
        event = UserCreatedMessage(user_id=uuid4())

        await publisher.publish(event)

        _, kwargs = broker.publish.await_args
        assert kwargs["subject"] == event.subject
