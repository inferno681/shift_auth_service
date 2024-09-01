import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.service import AuthService, producer, users


@pytest.fixture
def anyio_backend():
    """Бэкэнд для тестирования."""
    return 'asyncio'


@pytest.fixture
async def is_kafka_available():
    """Фикстура для проверки доступности Kafka."""
    return await producer.check()


@pytest.fixture(autouse=True)
def user_storage():
    """Фикстура для очистки хранилища перед каждым текстом."""
    users.clear()
    yield
    users.clear()


@pytest.fixture
async def client():
    """Фикстура клиента."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://127.0.0.1:8000/api/',
    ) as client:
        yield client


@pytest.fixture
def test_user():
    """Фикстура с данными пользователя."""
    return {'login': 'user', 'password': 'password'}


@pytest.fixture
def registration_link():
    """Фикстура со ссылкой на регистрацию."""
    return '/registration'


@pytest.fixture
def auth_link():
    """Фикстура со ссылкой на аутентификацию."""
    return '/auth'


@pytest.fixture
def check_link():
    """Фикстура со ссылкой на проверку токена."""
    return '/check_token'


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
def no_user_token():
    """Фикстура с токеном несуществующего пользователя."""
    return AuthService.generate_jwt_token(5)


@pytest.fixture
def check_health_link():
    """Фикстура со ссылкой на проверку готовности сервиса."""
    return '/healthz/ready'


@pytest.fixture
def verify_link():
    """Фикстура со ссылкой на загрузку фото."""
    return '/verify'


@pytest.fixture
def image_file():
    """Фикстура со ссылкой на файл с фото."""
    return 'src/tests/test_files/one_face.jpg'


@pytest.fixture
def wrong_file():
    """Фикстура со ссылкой файл не являющийся изображением."""
    return 'src/tests/test_files/wrong_file.txt'
