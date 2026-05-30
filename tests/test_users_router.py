import uuid

from httpx import AsyncClient


async def test_create_user(
    client: AsyncClient,
    user_service,
    uow,
    publisher,
    telemetry,
    mock_user,
):
    response = await client.post("/users", json={})

    assert response.status_code == 200

    data = response.json()

    assert data["id_"] == str(mock_user.id_)

    user_service.create_one.assert_awaited_once()

    uow.commit.assert_awaited_once()

    publisher.flush.assert_awaited_once()

    telemetry.metrics.users_counter.add.assert_called_once_with(1)

    telemetry.logger.info.assert_called_once_with(
        "user created",
        extra={
            "user_id": mock_user.id_,
        },
    )


async def test_get_user_success(
    client: AsyncClient,
    user_service,
    mock_user,
):
    response = await client.get(f"/users/{mock_user.id_}")

    assert response.status_code == 200

    data = response.json()

    assert data["id_"] == str(mock_user.id_)

    user_service.get_by_id.assert_awaited_once_with(
        id_=mock_user.id_,
    )


async def test_get_user_not_found(
    client: AsyncClient,
    user_service,
):
    user_id = uuid.uuid4()

    user_service.get_by_id.return_value = None

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 404

    data = response.json()

    assert "user" in str(data).lower()

    user_service.get_by_id.assert_awaited_once_with(
        id_=user_id,
    )


async def test_get_users(
    client: AsyncClient,
    user_service,
    mock_user,
):
    response = await client.get(
        "/users",
        params={
            "limit": 10,
            "offset": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id_"] == str(mock_user.id_)

    user_service.get_many.assert_awaited_once()

    args = user_service.get_many.await_args.args

    assert args[1] == 10
    assert args[2] == 20
