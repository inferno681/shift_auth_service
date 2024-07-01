import pytest


@pytest.fixture(autouse=True)
def user_storage():
    global users
    users = []
    yield


@pytest.fixture()
def user_data():
    return {"login": "user", "password": "password"}


@pytest.fixture()
def wrong_password_user_data():
    return {"login": "user", "password": "wrongpassword"}


@pytest.fixture()
def no_user_data():
    return {"login": "no_user", "password": "wrongpassword"}
