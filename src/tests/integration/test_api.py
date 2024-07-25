import pytest

from app.constants import USER_EXISTS_MESSAGE


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
    assert response.status_code == 200
    assert response.json()['token'] is None


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
