from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import config

engine = create_async_engine(
    url=config.database_url,
    echo=config.service.db_echo,
)

async_session = async_sessionmaker(bind=engine)
