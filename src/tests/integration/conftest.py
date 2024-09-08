import pytest

from app.main import app
from app.service import AuthService


@pytest.fixture()
async def delete_token():
    """Удаление токена из бд."""
    await app.state.redis.delete(1)


@pytest.fixture
def test_user():
    """Фикстура с данными пользователя."""
    return {'login': 'user', 'password': 'password'}


@pytest.fixture
def registration_link():
    """Фикстура со ссылкой на регистрацию."""
    return '/api/registration'


@pytest.fixture
def auth_link():
    """Фикстура со ссылкой на аутентификацию."""
    return '/api/auth'


@pytest.fixture
def check_link():
    """Фикстура со ссылкой на проверку токена."""
    return '/api/check_token'


@pytest.fixture
def metrics_link():
    """Фикстура со ссылкой на эндпоинт метрик."""
    return '/metrics/'


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
    return AuthService.generate_jwt_token(100)


@pytest.fixture
def check_health_link():
    """Фикстура со ссылкой на проверку готовности сервиса."""
    return '/api/healthz/ready'


@pytest.fixture
def verify_link():
    """Фикстура со ссылкой на загрузку фото."""
    return '/api/verify'


@pytest.fixture
def image_file():
    """Фикстура со ссылкой на файл с фото."""
    return 'src/tests/test_files/one_face.jpg'


@pytest.fixture
def wrong_file():
    """Фикстура со ссылкой файл не являющийся изображением."""
    return 'src/tests/test_files/wrong_file.txt'
