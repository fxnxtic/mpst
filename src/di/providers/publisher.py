from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker

from src.core.publisher import MessagePublisher

__all__ = ("MessagePublisherProvider",)


class MessagePublisherProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_message_publisher(self, broker: NatsBroker) -> MessagePublisher:
        return MessagePublisher(broker)
