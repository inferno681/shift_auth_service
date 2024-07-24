import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.service import users


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='module', autouse=True)
def user_storage():
    users.clear()
    yield
    users.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000/'
    ) as client:
        yield client


@pytest.fixture
def test_user():
    return {'login': 'login', 'password': 'password'}


@pytest.fixture
def registration_link():
    return '/registration'


@pytest.fixture
def auth_link():
    return '/auth'


@pytest.fixture
def link(request, registration_link, auth_link):
    if request.param == 'registration_link':
        return registration_link
    elif request.param == 'auth_link':
        return auth_link
