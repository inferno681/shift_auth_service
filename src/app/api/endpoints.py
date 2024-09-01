from fastapi import APIRouter

from app.api.schemes import (
    UserCreate,
    UserToken,
    UserTokenCheck,
    UserTokenCheckRequest,
)
from app.service import AuthService

router_auth = APIRouter()
router_check = APIRouter()


@router_auth.post('/registration', response_model=UserToken)
async def registration(user: UserCreate):
    """Эндпоинт регистрации пользователя."""
    return UserToken(
        token=AuthService.registration(
            login=user.login,
            password=user.password,
        ),
    )


@router_auth.post('/auth', response_model=UserToken)
async def authentication(user: UserCreate):
    """Эндпоинт аутентификации пользователя."""
    return UserToken(
        token=AuthService.authentication(
            login=user.login,
            password=user.password,
        ),
    )


@router_check.post('/check_token', response_model=UserTokenCheck)
async def check_token(token: UserTokenCheckRequest):
    """Эндпоинт проверки токена пользователя."""
    return AuthService.check_token(token.token)
