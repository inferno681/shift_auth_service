from fastapi import APIRouter

from config import config

from .endpoints import router_auth, router_check, router_healthz

router = APIRouter()
router.include_router(
    router_auth, tags=[config.service.tags_metadata_auth['name']]  # type: ignore
)
router.include_router(
    router_check, tags=[config.service.tags_metadata_check['name']]  # type: ignore
)

router.include_router(
    router_healthz, tags=[config.service.tags_metadata_health['name']]  # type: ignore
)
