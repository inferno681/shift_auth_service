import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router
from app.service import producer
from config import config

log = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запуск и остановка продьюсера кафка, создание директории для фото."""
    if not os.path.exists(config.service.photo_directory):
        os.makedirs(config.service.photo_directory)
    await producer.start()
    log.info('kafka producer started')
    yield
    await producer.stop()
    log.info('kafkaproducer stopped')


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
    lifespan=lifespan,
)  # type: ignore

app.include_router(router, prefix='/api')


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=config.service.host,  # type: ignore
        port=config.service.port,  # type: ignore
    )  # noqa:WPS432
