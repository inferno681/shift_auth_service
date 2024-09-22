import pytest

from app.main import app
from app.service import AuthService


@pytest.fixture()
async def delete_token():
    """Token removing from db."""
    await app.state.redis.delete(1)


@pytest.fixture
def test_user():
    """User test data."""
    return {'login': 'user', 'password': 'password'}


@pytest.fixture
def registration_link():
    """Registration link."""
    return '/api/registration'


@pytest.fixture
def auth_link():
    """Auth link."""
    return '/api/auth'


@pytest.fixture
def check_link():
    """Token check link."""
    return '/api/check_token'


@pytest.fixture
def metrics_link():
    """Metrics endpoint link."""
    return '/metrics/'


@pytest.fixture(
    params=(
        {'login': 'user', 'password': 'wrongpassword'},
        {'login': 'no_user', 'password': 'wrongpassword'},
    ),
    ids=('wrong_password', 'no_user'),
)
def wrong_user_data(request):
    """Incorrect user data."""
    return request.param


@pytest.fixture()
def no_user_token():
    """No user token."""
    return AuthService.generate_jwt_token(100)


@pytest.fixture
def check_health_link():
    """Health check link."""
    return '/api/healthz/ready'


@pytest.fixture
def verify_link():
    """Photo upload link."""
    return '/api/verify'


@pytest.fixture
def image_file():
    """Link to photo."""
    return 'src/tests/test_files/one_face.jpg'


@pytest.fixture
def wrong_file():
    """Wrong file link."""
    return 'src/tests/test_files/wrong_file.txt'
