import uvicorn
from fastapi import FastAPI, HTTPException, Request, status

from app.api import router
from app.service.exceptions import UserExistsError
from config import config

app = FastAPI(debug=config.service.debug)  # type: ignore

app.include_router(router)


@app.exception_handler(UserExistsError)
async def invalid_username_error_handler(
    request: Request,
    exc: UserExistsError,
):
    """Глобальный обработчик исключений для UserExistsError."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=config.service.host,  # type: ignore
        port=config.service.port,  # type: ignore
    )  # noqa:WPS432
