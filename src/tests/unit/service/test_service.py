import jwt
import pytest

from app.constants import INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE
from app.service import AuthService

auth_service = AuthService()


def test_decode_jwt_expired_token(expired_token):
    """Тест декодирования просроченного токена."""
    with pytest.raises(jwt.ExpiredSignatureError) as excinfo:
        AuthService.decode_jwt_token(expired_token)
    assert str(excinfo.value) == TOKEN_EXPIRED_MESSAGE


def test_decode_jwt_invalid_token():
    """Тест декодирования некорректного токена."""
    token = AuthService.generate_jwt_token(1)
    invalid_token = ''.join([token[:-5], '12345'])
    with pytest.raises(jwt.InvalidTokenError) as excinfo:
        AuthService.decode_jwt_token(invalid_token)
    assert str(excinfo.value) == INVALID_TOKEN_MESSAGE


def test_is_token_expired(expired_token):
    """Тест функции _is_token_expired."""
    assert AuthService.is_token_expired(expired_token) is True
