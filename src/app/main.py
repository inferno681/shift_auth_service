import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from jaeger_client import Config
from opentracing import (
    InvalidCarrierException,
    SpanContextCorruptedException,
    global_tracer,
    propagation,
    tags,
)
from prometheus_client import make_asgi_app

from app.api import router
from app.metrics import (
    AUTH_RESULT,
    READY_PROBE,
    REQUEST_COUNT,
    REQUEST_DURATION,
)
from app.service import producer
from config import config

log = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запуск и остановка продьюсера кафка, создание директории для фото."""
    if not os.path.exists(config.service.photo_directory):  # type: ignore
        os.makedirs(config.service.photo_directory)  # type: ignore
    await producer.start()
    log.info('kafka producer started')
    tracer_config = Config(
        config={
            'sampler': {
                'type': config.jaeger.sampler_type,  # type: ignore
                'param': config.jaeger.sampler_param,  # type: ignore
            },
            'local_agent': {
                'reporting_host': config.jaeger.host,  # type: ignore
                'reporting_port': config.jaeger.port,  # type: ignore
            },
            'logging': config.jaeger.logging,  # type: ignore
        },
        service_name=config.jaeger.service_name,  # type: ignore
        validate=True,
    )
    tracer = tracer_config.initialize_tracer()
    app.state.jaeger_tracer = tracer
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


@app.middleware('http')
async def tracing_middleware(request: Request, call_next):
    """Middleware для трейсинга."""
    path = request.url.path
    if path.endswith(('/ready', '/metrics/', '/docs', '/openapi.json')):
        return await call_next(request)
    try:
        span_ctx = global_tracer().extract(
            propagation.Format.HTTP_HEADERS,
            dict(request.headers),
        )
    except (InvalidCarrierException, SpanContextCorruptedException):
        span_ctx = None
    span_tags = {
        tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
        tags.HTTP_METHOD: request.method,
        tags.HTTP_URL: str(request.url),
    }
    with global_tracer().start_active_span(
        f'transactions_{request.method}_{request.url.path}',
        child_of=span_ctx,
        tags=span_tags,
    ) as scope:
        response = await call_next(request)
        scope.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
        return response


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=config.service.host,  # type: ignore
        port=config.service.port,  # type: ignore
    )  # noqa:WPS432
