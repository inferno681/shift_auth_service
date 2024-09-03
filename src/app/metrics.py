from typing import Final

from prometheus_client import Counter, Histogram

SERVICE_PREFIX: Final[str] = 'stakrotckii_auth'
REQUEST_COUNT = Counter(
    name=f'{SERVICE_PREFIX}_request_count',
    documentation='Total number of requests',
    labelnames=['method', 'endpoint', 'status'],
)
REQUEST_DURATION = Histogram(
    name=f'{SERVICE_PREFIX}_request_duration',
    documentation='Time spend processing request',
    labelnames=['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 2.5, 5, 10),
)

READY_PROBE = Counter(
    name=f'{SERVICE_PREFIX}_ready_probe',
    documentation='Ready probe metric',
    labelnames=['status'],
)

AUTH_RESULT = Counter(
    name=f'{SERVICE_PREFIX}_auth_result',
    documentation='Auth result metric',
    labelnames=['status'],
)
