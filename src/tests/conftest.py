from datetime import datetime, timedelta

import pytest

from app.main import users


@pytest.fixture(autouse=True)
def user_storage():
    users.clear()
    yield
    users.clear()


@pytest.fixture()
def user_data():
    return {"login": "user", "password": "password"}


@pytest.fixture()
def wrong_password_user_data():
    return {"login": "user", "password": "wrongpassword"}


@pytest.fixture()
def no_user_data():
    return {"login": "no_user", "password": "wrongpassword"}


@pytest.fixture()
def expired_payload():
    return {
        "id": 1,
        "exp": (datetime.now() - timedelta(seconds=1)).timestamp(),
    }


@pytest.fixture()
def id_for_payload():
    return 1
