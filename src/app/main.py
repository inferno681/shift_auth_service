from contextlib import asynccontextmanager
from app.service import producer
import uvicorn
from fastapi import FastAPI

from app.api import router
from config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запуск и остановка продьюсера кафка."""
    await producer.start()
    print('started')
    yield
    await producer.stop()


tags_metadata = [
    config.service.tags_metadata_auth,  # type: ignore
    config.service.tags_metadata_check,  # type: ignore
    config.service.tags_metadata_health,  # type: ignore
    config.service.tags_metadata_verify,  # type: ignore
]
app = FastAPI(
    title=config.service.title,  # type: ignore
    description=config.service.description,  # type: ignore
    tags_metadata=tags_metadata,
    debug=config.service.debug,  # type: ignore
)  # type: ignore

app.include_router(router, prefix='/api')


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=config.service.host,  # type: ignore
        port=config.service.port,  # type: ignore
    )  # noqa:WPS432
