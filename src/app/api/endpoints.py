from fastapi import APIRouter

from app.api.schemas import UserCreate, Userjwt
from app.service import AuthService

router = APIRouter()


@router.post('/registration', response_model=Userjwt)
async def registration(user: UserCreate):
    """Эндпоинт регистрации пользователя."""
    return Userjwt(
        jwt=AuthService.registration(
            login=user.login,
            password=user.password,
        ),
    )


@router.post('/auth', response_model=Userjwt)
async def authentication(user: UserCreate):
    """Эндпоинт аутентификации пользователя."""
    return Userjwt(
        jwt=AuthService.authentication(
            login=user.login,
            password=user.password,
        ),
    )
