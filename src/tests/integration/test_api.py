import pytest
from sqlalchemy import text

from app.constants import (
    KAFKA_RESPONSE,
    USER_EXISTS_MESSAGE,
    USER_NOT_FOUND,
    WRONG_IMAGE_FORMAT,
)
from app.db.database import engine
from app.main import app
from app.metrics import (
    AUTH_RESULT,
    READY_PROBE,
    REQUEST_COUNT,
    REQUEST_DURATION,
)


@pytest.mark.anyio
async def test_registration(client, test_user, registration_link):
    """Тест регистрации пользователя."""
    response = await client.post(registration_link, json=test_user)
    assert response.status_code == 200
    async with engine.connect() as conn:
        user = await conn.execute(
            text('SELECT login FROM "user" WHERE id = 1'),
        )
        assert test_user['login'] == user.scalar_one_or_none()
        assert response.json()['token'] == await app.state.redis.get(1)


@pytest.mark.anyio
async def test_authentication(client, test_user, auth_link):
    """Тест аутентификации пользователя."""
    response = await client.post(auth_link, json=test_user)
    assert response.status_code == 200
    assert 'token' in response.json()
    async with engine.connect() as conn:
        user = await conn.execute(
            text('SELECT login FROM "user" WHERE id = 1'),
        )
        assert test_user['login'] == user.scalar_one_or_none()
        assert response.json()['token'] == await app.state.redis.get(1)


@pytest.mark.anyio
async def test_registration_existing_user(
    client,
    test_user,
    registration_link,
):
    """Тест регистрации уже существующего пользователя."""
    response = await client.post(registration_link, json=test_user)
    assert response.status_code == 400
    assert response.json()['detail'] == USER_EXISTS_MESSAGE.format(
        login=test_user['login'],
    )


@pytest.mark.anyio
async def test_wrong_login(
    auth_link,
    client,
    wrong_user_data,
):
    """Тест аутентификации пользователя с некорректными данными."""
    response = await client.post(auth_link, json=wrong_user_data)
    assert response.status_code == 404
    assert response.json()['detail'] == USER_NOT_FOUND


@pytest.mark.anyio
async def test_token_check(client, auth_link, test_user, check_link):
    """Тест проверки токена."""
    response = await client.post(auth_link, json=test_user)
    token = response.json()['token']
    response = await client.post(check_link, json={'token': token})
    assert response.status_code == 200
    assert response.json()['is_token_valid'] is True


@pytest.mark.anyio
async def test_no_user_token_check(client, check_link, no_user_token):
    """Тест проверки токена несуществующего пользователя."""
    response = await client.post(check_link, json={'token': no_user_token})
    assert response.status_code == 200
    assert response.json()['is_token_valid'] is False


@pytest.mark.anyio
async def test_check_healthz(client, check_health_link):
    """Тест проверки запущени ли сервис."""
    response = await client.get(check_health_link)
    assert response.status_code == 200
    assert response.json()['is_ready'] is True


@pytest.mark.anyio
async def test_photo_upload(
    client,
    verify_link,
    image_file,
    test_user,
    auth_link,
    check_link,
):
    """Тест загрузки фото."""
    response = await client.post(auth_link, json=test_user)
    token = response.json()['token']
    response = await client.post(check_link, json={'token': token})
    user_id = response.json()['user_id']
    response = await client.post(
        verify_link,
        data={'user_id': user_id},
        files={'file': ('one_face.jpg', image_file, 'image/jpeg')},
    )

    assert response.status_code == 200
    assert response.json()['message'] == KAFKA_RESPONSE


@pytest.mark.anyio
async def test_wrong_file_upload(client, verify_link, wrong_file):
    """Тест загрузки фото."""
    response = await client.post(
        verify_link,
        data={'user_id': 1},
        files={'file': ('wrong_file.txt', wrong_file, 'image/jpeg')},
    )
    assert response.status_code == 400
    assert response.json()['detail'] == WRONG_IMAGE_FORMAT.format(
        extension=wrong_file[-4:],
    )


@pytest.mark.anyio
async def test_authentication_without_token(
    client,
    test_user,
    auth_link,
    delete_token,
):
    """Тест аутентификации пользователя без токена в бд."""
    assert await app.state.redis.get(1) is None
    response = await client.post(auth_link, json=test_user)
    assert response.status_code == 200
    assert 'token' in response.json()
    assert response.json()['token'] is not None


@pytest.mark.anyio
async def test_metrics(client, metrics_link):
    """Тест эндпоинта для сбора метрик."""
    response = await client.get(metrics_link)
    assert response.status_code == 200
    assert READY_PROBE._documentation in response.text
    assert REQUEST_COUNT._documentation in response.text
    assert REQUEST_DURATION._documentation in response.text
    assert AUTH_RESULT._documentation in response.text
