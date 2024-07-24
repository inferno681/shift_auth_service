from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Схема регистрации пользователя."""

    login: str = Field(
        description='Логин',
        min_length=3,
        max_length=20,  # noqa:WPS432
        pattern='^[a-zA-Z0-9]+$',
    )
    password: str = Field(
        description='Пароль',
        min_length=6,
        max_length=100,
    )


class UserToken(BaseModel):
    """Схема отдачи токена."""

    token: str | None = None


class UserTokenCheck(BaseModel):
    """Схема проверки токена."""

    is_token_valid: bool
