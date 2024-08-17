from datetime import datetime, timedelta

import jwt
import pytest

from app.service import AuthService
from config import config


@pytest.fixture()
def user_data():
    """Фикстура с данными пользователя."""
    return {'login': 'user', 'password': 'password'}


@pytest.fixture()
def registred_user_token(user_data):
    """Фикстура с зарегистрированным пользователем."""
    return AuthService.registration(**user_data)


@pytest.fixture()
def none_token_in_storage(registred_user_token):
    """Фикстура с None токеном в хранилище."""
    tokens[0].token = None


@pytest.fixture()
def no_token_in_storage(registred_user_token):
    """Фикстура без токена в хранилище."""
    tokens.clear()


@pytest.fixture(
    params=(
        {'login': 'user', 'password': 'wrongpassword'},
        {'login': 'no_user', 'password': 'wrongpassword'},
    ),
    ids=('wrong_password', 'no_user'),
)
def wrong_user_data(request):
    """Фикстура с некорректными данными пользователя."""
    return request.param


@pytest.fixture()
def expired_payload():
    """Фикстура с данными для просроченного токена."""
    return {
        'user_id': 1,
        'exp': (datetime.now() - timedelta(seconds=1)).timestamp(),
    }


@pytest.fixture()
def id_for_payload():
    """Фикстура с ID пользователя для токена."""
    return 1


@pytest.fixture()
def expired_token_in_storage(registred_user_token, expired_payload):
    """Фикстура с истекшим токеном в хранилище."""
    expired_token = jwt.encode(
        expired_payload,
        config.SECRET.get_secret_value(),
        algorithm='HS256',
    )
    tokens[0].token = expired_token


@pytest.fixture()
def wrong_token_in_storage(
    request,
    none_token_in_storage,
    expired_token_in_storage,
):
    """Фикстура для подстановки некорректных токенов."""
    if request.param == 'none_token_in_storage':
        return none_token_in_storage
    elif request.param == 'expired_token':
        return expired_token_in_storage
