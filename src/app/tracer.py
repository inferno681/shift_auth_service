from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from config import config


def setup_tracer():
    """Функция для запуска трейсера."""
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: 'stakrotckii_auth'}),
        ),
    )

    tracer_provider = trace.get_tracer_provider()
    jaeger_exporter = JaegerExporter(
        agent_host_name=config.service.tracer_host,  # type: ignore
        agent_port=config.service.tracer_port,  # type: ignore
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
