from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import count

import bcrypt
import jwt

from app.constants import (
    ENCODING_FORMAT,
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
)
from app.service.exceptions import UserExistsError
from config import config

users = []  # type: ignore
_id_counter = count(1)


@dataclass
class User:
    """Класс пользователя."""

    id: int = field(default_factory=lambda: next(_id_counter), init=False)
    login: str
    hashed_password: str
    token: str = ''


class AuthService:
    """Сервис авторизации."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширование пароля."""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(ENCODING_FORMAT), salt)
        return hashed_password.decode(ENCODING_FORMAT)

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Проверка пароля."""
        return bcrypt.checkpw(
            password.encode(ENCODING_FORMAT),
            hashed_password.encode(ENCODING_FORMAT),
        )

    @staticmethod
    def registration(login, password):
        """Регистрация пользователя."""
        if next((user for user in users if user.login == login), None):
            raise UserExistsError(USER_EXISTS_MESSAGE.format(login=login))
        hashed_password = AuthService.hash_password(password)
        user = User(login=login, hashed_password=hashed_password)
        user.token = AuthService.generate_jwt_token(user.id)
        users.append(user)
        return user.token

    @staticmethod
    def authentication(login: str, password: str) -> str | None:
        """Аутентификация пользователя."""
        user = next((user for user in users if user.login == login), None)
        if user and AuthService.check_password(password, user.hashed_password):
            user.token = AuthService.generate_jwt_token(user.id)
            return user.token
        return None

    @staticmethod
    def generate_jwt_token(user_id: int) -> str:
        """Генерация JWT токена."""
        payload = {
            'id': user_id,
            'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        }
        return jwt.encode(
            payload,
            config.SECRET.get_secret_value(),
            algorithm='HS256',
        )

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Декодирование JWT токена."""
        try:
            return jwt.decode(
                token,
                config.SECRET.get_secret_value(),
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(TOKEN_EXPIRED_MESSAGE)
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError(INVALID_TOKEN_MESSAGE)

    @staticmethod
    def check_token(token: str) -> bool:
        """Проверка токена."""
        user_id = AuthService.decode_jwt_token(token)['id']
        user = next((user for user in users if user.id == user_id), None)
        if not user:
            return False
        return user.token == token
