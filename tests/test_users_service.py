from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from src.services.users.service import UserService
from src.services.users.types.messages import UserCreatedMessage
from src.services.users.types.schemas import UserCS, UserFilters, UserSchema


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def publisher():
    mock = AsyncMock()
    mock.collect = Mock()
    mock.discard = Mock(return_value=0)
    return mock


@pytest.fixture
def mock_dao():
    return AsyncMock()


@pytest.fixture
def orm_user():
    user = Mock()
    user.id_ = uuid4()
    user.deleted = False
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


@pytest.fixture
def user_service(session, publisher, mock_dao):
    with patch("src.services.users.service.UserDAO") as mock_dao_cls:
        mock_dao_cls.return_value = mock_dao
        svc = UserService(session=session, publisher=publisher)
        yield svc, mock_dao


class TestCreateOne:
    async def test_creates_user_and_collects_event(self, user_service, orm_user):
        svc, mock_dao = user_service
        mock_dao.create.return_value = orm_user

        result = await svc.create_one(UserCS())

        assert isinstance(result, UserSchema)
        assert result.deleted is False

        mock_dao.create.assert_awaited_once()
        create_call_arg = mock_dao.create.await_args.kwargs["data"]
        assert isinstance(create_call_arg, UserCS)
        assert create_call_arg.id_ is not None

        svc._publisher.collect.assert_called_once()
        collect_arg = svc._publisher.collect.call_args[0][0]
        assert isinstance(collect_arg, UserCreatedMessage)
        assert collect_arg.user_id == create_call_arg.id_

    async def test_create_with_kwargs(self, user_service, orm_user):
        svc, mock_dao = user_service
        mock_dao.create.return_value = orm_user

        result = await svc.create_one(name="test")

        assert isinstance(result, UserSchema)
        mock_dao.create.assert_awaited_once()


class TestGetById:
    async def test_returns_user_when_found(self, user_service, orm_user):
        svc, mock_dao = user_service
        mock_dao.get_by_id.return_value = orm_user

        result = await svc.get_by_id(id_=orm_user.id_)

        assert isinstance(result, UserSchema)
        assert result.id_ == orm_user.id_

        mock_dao.get_by_id.assert_awaited_once_with(pk=orm_user.id_)

    async def test_returns_none_when_not_found(self, user_service):
        svc, mock_dao = user_service
        mock_dao.get_by_id.return_value = None

        result = await svc.get_by_id(id_=uuid4())

        assert result is None

        mock_dao.get_by_id.assert_awaited_once()


class TestGetMany:
    async def test_returns_users_with_pagination(self, user_service, orm_user):
        svc, mock_dao = user_service
        mock_dao.get_many.return_value = ([orm_user], 1)

        result = await svc.get_many(filters=None, limit=10, offset=20)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], UserSchema)

        mock_dao.get_many.assert_awaited_once()
        args = mock_dao.get_many.await_args.args
        pagination = args[0]
        assert pagination.limit == 10
        assert pagination.offset == 20
        assert args[1] is None

    async def test_returns_empty_list(self, user_service):
        svc, mock_dao = user_service
        mock_dao.get_many.return_value = ([], 0)

        result = await svc.get_many()

        assert isinstance(result, list)
        assert len(result) == 0

    async def test_accepts_filters(self, user_service, orm_user):
        svc, mock_dao = user_service
        mock_dao.get_many.return_value = ([orm_user], 1)
        filters = UserFilters(deleted=False)

        result = await svc.get_many(filters=filters)

        assert len(result) == 1
        mock_dao.get_many.assert_awaited_once()
        passed_filters = mock_dao.get_many.await_args.args[1]
        assert passed_filters is filters
