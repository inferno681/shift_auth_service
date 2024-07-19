from datetime import datetime, timedelta

import pytest

from app.service import users


@pytest.fixture(autouse=True)
def user_storage():
    """Фикстура для очистки хранилища перед каждым текстом."""
    users.clear()
    yield
    users.clear()


@pytest.fixture()
def user_data():
    """Фикстура с данными пользователя."""
    return {'login': 'user', 'password': 'password'}


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
