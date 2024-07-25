import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.api import router
from app.service.exceptions import UserExistsError

app = FastAPI()

app.include_router(router)


@app.exception_handler(ExpiredSignatureError)
async def expired_signature_error_handler(
    request: Request,
    exc: ExpiredSignatureError,
):
    """Глобальный обработчик исключений для ExpiredSignatureError."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(exc),
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_error_handler(
    request: Request,
    exc: InvalidTokenError,
):
    """Глобальный обработчик исключений для InvalidTokenError."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(exc),
    )


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
    uvicorn.run(app, host='localhost', port=8000)  # noqa:WPS432
