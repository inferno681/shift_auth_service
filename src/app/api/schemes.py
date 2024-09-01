from pydantic import BaseModel, Field, PositiveInt

from app.constants import KAFKA_RESPONSE


class UserCreate(BaseModel):
    """Схема регистрации пользователя."""

    login: str = Field(
        description='Логин',
        min_length=3,
        max_length=20,  # noqa:WPS432
        pattern='^[a-zA-Z0-9._-]+$',
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

    user_id: PositiveInt | None = None
    is_token_valid: bool


class UserTokenCheckRequest(BaseModel):
    """Схема передачи токена для проверки."""

    token: str


class IsReady(BaseModel):
    """Схема ответа health check."""

    is_ready: bool


class KafkaResponse(BaseModel):
    """Ответ на отправку фото."""

    message: str = KAFKA_RESPONSE
