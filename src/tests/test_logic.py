import jwt
import pytest

from app.config import config
from app.constants import (
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
)
from app.main import AuthService, users

auth_service = AuthService()


def test_registration(user_data):
    """Тест регистрации пользователя."""
    assert auth_service.registration(**user_data) is not None
    assert len(users) == 1
    assert users[0].login == user_data['login']


def test_registration_existing_user(user_data):
    """Тест регистрации уже существующего пользователя."""
    auth_service.registration(**user_data)
    response = auth_service.registration(**user_data)
    assert response == USER_EXISTS_MESSAGE.format(login=user_data['login'])


def test_authentication(user_data):
    """Тест аутентификации пользователя."""
    auth_service.registration(**user_data)
    assert auth_service.authentication(**user_data) is not None


def test_wrong_authentication(user_data, wrong_user_data):
    """Тест аутентификации пользователя с некорректными данными."""
    auth_service.registration(**user_data)
    assert auth_service.authentication(**wrong_user_data) is None


def test_generate_jwt_token(id_for_payload):
    """Тест генерации jwt токена."""
    token = AuthService.generate_jwt_token(id_for_payload)
    decoded_jwt = AuthService.decode_jwt_token(token)
    assert decoded_jwt['id'] == 1
    assert 'exp' in decoded_jwt


def test_decode_jwt_expired_token(expired_payload):
    """Тест декодирования просроченного токена."""
    expired_token = jwt.encode(
        expired_payload,
        config.SECRET.get_secret_value(),
        algorithm='HS256',
    )
    with pytest.raises(jwt.ExpiredSignatureError) as excinfo:
        AuthService.decode_jwt_token(expired_token)
    assert str(excinfo.value) == TOKEN_EXPIRED_MESSAGE


def test_decode_jwt_invalid_token(id_for_payload):
    """Тест декодирования некорректного токена."""
    token = AuthService.generate_jwt_token(id_for_payload)
    invalid_token = ''.join([token[:-5], '12345'])
    with pytest.raises(jwt.InvalidTokenError) as excinfo:
        AuthService.decode_jwt_token(invalid_token)
    assert str(excinfo.value) == INVALID_TOKEN_MESSAGE
