import jwt
import pytest

from app.constants import (
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
)
from app.service import AuthService, users
from app.service.exceptions import UserExistsError
from config import config

auth_service = AuthService()


def test_registration(user_data):
    """Тест регистрации пользователя."""
    assert auth_service.registration(**user_data) is not None
    assert len(users) == 1
    assert users[0].login == user_data['login']


def test_registration_existing_user(user_data, registred_user_token):
    """Тест регистрации уже существующего пользователя."""
    with pytest.raises(UserExistsError) as excinfo:
        auth_service.registration(**user_data)
    assert str(excinfo.value) == USER_EXISTS_MESSAGE.format(
        login=user_data['login'],
    )


def test_authentication(user_data):
    """Тест аутентификации пользователя."""
    auth_service.registration(**user_data)
    assert auth_service.authentication(**user_data) is not None


def test_wrong_authentication(user_data, wrong_user_data):
    """Тест аутентификации пользователя с некорректными данными."""
    auth_service.registration(**user_data)
    assert auth_service.authentication(**wrong_user_data) is None


@pytest.mark.parametrize(
    'wrong_token_in_storage',
    [
        pytest.param('none_token_in_storage', id='none_token_in_storage'),
        pytest.param('expired_token', id='expired_token'),
    ],
    indirect=True,
)
def test_wrong_token_authentication(user_data, wrong_token_in_storage):
    """Тест атентификации с просроченным и None токенами  в хранилище."""
    token = auth_service.authentication(**user_data)
    assert token is not None


def test_no_token_in_storage_authentication(user_data, no_token_in_storage):
    """Тест атентификации с отсутствием токена в хранилище."""
    token = auth_service.authentication(**user_data)
    assert token is not None


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


def test_check_token(user_data):
    """Тест проверки токена."""
    token = auth_service.registration(**user_data)
    response = auth_service.check_token(token)
    assert response.user_id is not None
    assert response.is_token_valid is True


def test_check_no_user_token(id_for_payload):
    """Тест проверки токена несуществующего пользователя."""
    token = AuthService.generate_jwt_token(id_for_payload)
    assert auth_service.check_token(token).is_token_valid is False


def test_check_expired_token(expired_token_in_storage):
    """Тест проверки просроченного токена."""
    assert (
        auth_service.check_token(expired_token_in_storage).is_token_valid
        is False
    )
