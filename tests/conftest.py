import sys
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from src.core.exceptions import AppError
from src.core.publisher import MessagePublisher
from src.core.telemetry import Telemetry
from src.database.uow import UnitOfWork
from src.services.users.service import UserService
from src.services.users.types.schemas import UserSchema
from src.services.users.web import router


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


sys.modules["opentelemetry.instrumentation.faststream"] = Mock()


@pytest.fixture
def mock_user() -> UserSchema:
    return UserSchema(
        id_=uuid.uuid4(),
        deleted=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def user_service(mock_user: UserSchema) -> AsyncMock:
    svc = AsyncMock(spec=UserService)

    svc.create_one.return_value = mock_user
    svc.get_by_id.return_value = mock_user
    svc.get_many.return_value = [mock_user]

    return svc


@pytest.fixture
def uow() -> AsyncMock:
    mock = AsyncMock(spec=UnitOfWork)

    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None

    return mock


@pytest.fixture
def publisher() -> AsyncMock:
    mock = AsyncMock(spec=MessagePublisher)

    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None

    return mock


@pytest.fixture
def telemetry() -> MagicMock:
    mock = MagicMock(spec=Telemetry)
    mock.logger = Mock()

    return mock


@pytest.fixture
def app(
    user_service: AsyncMock,
    uow: AsyncMock,
    publisher: AsyncMock,
    telemetry: MagicMock,
) -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(router)

    class TestProvider(Provider):
        @provide(scope=Scope.REQUEST)
        def provide_user_service(self) -> UserService:
            return cast(UserService, user_service)

        @provide(scope=Scope.REQUEST)
        def provide_uow(self) -> UnitOfWork:
            return cast(UnitOfWork, uow)

        @provide(scope=Scope.REQUEST)
        def provide_publisher(self) -> MessagePublisher:
            return cast(MessagePublisher, publisher)

        @provide(scope=Scope.REQUEST)
        def provide_telemetry(self) -> Telemetry:
            return cast(Telemetry, telemetry)

    container = make_async_container(TestProvider())

    setup_dishka(container=container, app=app)

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
