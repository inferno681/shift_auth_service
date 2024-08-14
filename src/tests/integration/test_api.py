from unittest.mock import patch

import pytest
from asgi_lifespan import LifespanManager

from app.constants import (
    KAFKA_RESPONSE,
    USER_EXISTS_MESSAGE,
    USER_NOT_FOUND,
    WRONG_IMAGE_FORMAT,
)
from app.main import app
from app.service import users


@pytest.mark.anyio
async def test_registration(client, test_user, registration_link):
    """Тест регистрации пользователя."""
    response = await client.post(registration_link, json=test_user)
    assert response.status_code == 200
    assert 'token' in response.json()
    assert response.json()['token'] is not None


@pytest.mark.anyio
async def test_authentication(client, test_user, auth_link, registration_link):
    """Тест аутентификации пользователя."""
    await client.post(registration_link, json=test_user)
    response = await client.post(auth_link, json=test_user)
    assert response.status_code == 200
    assert 'token' in response.json()
    assert response.json()['token'] is not None


@pytest.mark.anyio
async def test_registration_existing_user(
    client,
    test_user,
    registration_link,
):
    """Тест регистрации уже существующего пользователя."""
    await client.post(registration_link, json=test_user)
    response = await client.post(registration_link, json=test_user)
    assert response.status_code == 400
    assert response.json()['detail'] == USER_EXISTS_MESSAGE.format(
        login=test_user['login'],
    )


@pytest.mark.anyio
async def test_wrong_login(
    auth_link,
    client,
    registration_link,
    wrong_user_data,
    test_user,
):
    """Тест аутентификации пользователя с некорректными данными."""
    await client.post(registration_link, json=test_user)
    response = await client.post(auth_link, json=wrong_user_data)
    assert response.status_code == 404
    assert response.json()['detail'] == USER_NOT_FOUND


@pytest.mark.anyio
async def test_token_check(client, registration_link, test_user, check_link):
    """Тест проверки токена."""
    response = await client.post(registration_link, json=test_user)
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
    is_kafka_available,
    test_user,
    registration_link,
):
    """Тест загрузки фото."""
    response = await client.post(registration_link, json=test_user)
    if is_kafka_available:
        async with LifespanManager(app):
            response = await client.post(
                verify_link,
                data={'user_id': users[0].id},
                files={'file': ('one_face.jpg', image_file, 'image/jpeg')},
            )
    else:
        with patch('app.api.endpoints.producer.send_message') as mock_kafka:
            response = await client.post(
                verify_link,
                data={'user_id': users[0].id},
                files={'file': ('one_face.jpg', image_file, 'image/jpeg')},
            )
            mock_kafka.assert_called_once
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
