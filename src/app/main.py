import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app

from app.api import router
from app.metrics import (
    AUTH_RESULT,
    READY_PROBE,
    REQUEST_COUNT,
    REQUEST_DURATION,
)
from app.service import producer
from app.tracer import setup_tracer
from config import config

log = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запуск и остановка продьюсера кафка, создание директории для фото."""
    if not os.path.exists(config.service.photo_directory):  # type: ignore
        os.makedirs(config.service.photo_directory)  # type: ignore
    await producer.start()
    log.info('kafka producer started')
    setup_tracer()
    log.info('tracer started')
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
FastAPIInstrumentor.instrument_app(app)
metrics_app = make_asgi_app()
app.mount('/metrics', metrics_app)


@app.middleware('http')
async def metrics_middleware(request: Request, call_next):
    """Middleware для формирования метрик."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(process_time)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    if request.url.path == '/api/healthz/ready':
        READY_PROBE.labels(status=response.status_code).inc()
    if request.url.path == '/api/auth':
        AUTH_RESULT.labels(status=response.status_code).inc()

    return response


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=config.service.host,  # type: ignore
        port=config.service.port,  # type: ignore
    )  # noqa:WPS432
