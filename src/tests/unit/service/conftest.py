from datetime import datetime, timedelta

import jwt
import pytest

from config import config


@pytest.fixture()
def expired_payload():
    """Expired token  payload."""
    return {
        'user_id': 1,
        'exp': (datetime.now() - timedelta(seconds=1)).timestamp(),
    }


@pytest.fixture()
def expired_token(expired_payload):
    """Expired token."""
    return jwt.encode(
        expired_payload,
        config.SECRET.get_secret_value(),
        algorithm='HS256',
    )
