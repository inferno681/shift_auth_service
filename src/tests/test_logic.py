import jwt
import pytest

from app.config import config
from app.constants import *
from app.main import AuthService, users

auth_service = AuthService()


def test_registration(user_data):
    jwt = auth_service.registration(**user_data)
    assert jwt is not None
    assert len(users) == 1
    assert users[0].login == user_data["login"]


def test_registration_existing_user(user_data):
    auth_service.registration(**user_data)
    response = auth_service.registration(**user_data)
    assert response == USER_EXISTS.format(login=user_data["login"])


def test_authentication(user_data):
    auth_service.registration(**user_data)
    jwt = auth_service.authentication(**user_data)
    assert jwt is not None


def test_wrong_authentication(user_data, wrong_user_data):
    auth_service.registration(**user_data)
    jwt = auth_service.authentication(**wrong_user_data)
    assert jwt is None


def test_generate_jwt_token(id_for_payload):
    jwt = AuthService.generate_jwt_token(id_for_payload)
    decoded_jwt = AuthService.decode_jwt_token(jwt)
    assert decoded_jwt["id"] == 1
    assert "exp" in decoded_jwt


def test_decode_jwt_expired_token(expired_payload):
    expired_token = jwt.encode(
        expired_payload, config.SECRET.get_secret_value(), algorithm="HS256"
    )
    with pytest.raises(jwt.ExpiredSignatureError) as excinfo:
        AuthService.decode_jwt_token(expired_token)
    assert str(excinfo.value) == TOKEN_EXPIRED


def test_decode_jwt_invalid_token(id_for_payload):
    token = AuthService.generate_jwt_token(id_for_payload)
    invalid_token = token[:-5] + "12345"
    with pytest.raises(jwt.InvalidTokenError) as excinfo:
        AuthService.decode_jwt_token(invalid_token)
    assert str(excinfo.value) == INVALID_TOKEN
