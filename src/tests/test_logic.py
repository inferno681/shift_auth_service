from datetime import datetime, timedelta

import jwt
import pytest

from app.config import config
from app.constants import *
from app.main import AuthService, users


def test_registration(user_data):
    auth_service = AuthService()
    jwt = auth_service.registration(**user_data)
    assert jwt is not None
    assert len(users) == 1
    assert users[0].login == user_data["login"]


def test_registration_existing_user(user_data):
    auth_service = AuthService()
    auth_service.registration(**user_data)
    response = auth_service.registration(**user_data)
    assert response == USER_EXISTS.format(login=user_data["login"])


def test_authentication(user_data):
    auth_service = AuthService()
    auth_service.registration(**user_data)
    jwt = auth_service.authenticate(**user_data)
    assert jwt is not None


def test_authentication_wrong_password(user_data, wrong_password_user_data):
    auth_service = AuthService()
    auth_service.registration(**user_data)
    jwt = auth_service.authenticate(**wrong_password_user_data)
    assert jwt is None


def test_authentication_no_user(user_data, no_user_data):
    auth_service = AuthService()
    auth_service.registration(**user_data)
    jwt = auth_service.authenticate(**no_user_data)
    assert jwt is None


def test_generate_jwt_token():
    jwt = AuthService.generate_jwt_token(1)
    decoded_jwt = AuthService.decode_jwt_token(jwt)
    assert decoded_jwt["id"] == 1
    assert "exp" in decoded_jwt


def test_decode_jwt_token_exeptions():
    expired_payload = {
        "id": 1,
        "exp": (datetime.now() - timedelta(seconds=1)).timestamp(),
    }
    expired_token = jwt.encode(
        expired_payload, config.SECRET.get_secret_value(), algorithm="HS256"
    )
    try:
        AuthService.decode_jwt_token(expired_token)
    except jwt.ExpiredSignatureError:
        assert True
    except jwt.InvalidTokenError:
        assert True
