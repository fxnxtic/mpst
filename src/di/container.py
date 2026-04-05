from dishka import AsyncContainer, Provider, make_async_container


def create_container(providers: list[Provider]) -> AsyncContainer:
    return make_async_container(*providers)
