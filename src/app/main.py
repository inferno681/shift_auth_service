import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.api import router
from app.constants import INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE

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
        detail=TOKEN_EXPIRED_MESSAGE,
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_error_handler(
    request: Request,
    exc: InvalidTokenError,
):
    """Глобальный обработчик исключений для InvalidTokenError."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INVALID_TOKEN_MESSAGE,
    )


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)  # noqa:WPS432
