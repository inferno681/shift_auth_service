from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import config

engine = create_async_engine(
    url=config.database_url,  # type: ignore
    echo=config.service.db_echo,  # type: ignore
)

async_session = async_sessionmaker(bind=engine)


async def get_async_session():
    """Async session generator."""
    async with async_session() as session:
        yield session
