import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base, get_async_session
from app.service import AuthService, producer


@pytest.fixture(scope='session')
async def session():
    """Получение сессии для подключения к бд."""
    async for session in get_async_session():
        yield session


@pytest.fixture(scope='session', autouse=True)
async def clear_database(session: AsyncSession):
    """Фикстура для очистки всех данных из базы данных перед тестами."""
    async with session.begin():
        await session.execute(text('SET session_replication_role = replica;'))
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        for table in Base.metadata.sorted_tables:
            await session.execute(
                text(f'ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1;'),
            )
        await session.execute(text('SET session_replication_role = DEFAULT;'))
        await session.commit()


@pytest.fixture(scope='session')
def anyio_backend():
    """Бэкэнд для тестирования."""
    return 'asyncio'


@pytest.fixture
async def is_kafka_available():
    """Фикстура для проверки доступности Kafka."""
    return await producer.check()


@pytest.fixture
async def client():
    """Фикстура клиента."""
    async with AsyncClient(
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
    return AuthService.generate_jwt_token(100)


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
