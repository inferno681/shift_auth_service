from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import count

import bcrypt
import jwt

from app.config import config
from app.constants import *

users = []  # type: ignore


@dataclass
class User:
    """Класс пользователя"""

    id: int = field(default_factory=count(1).__next__, init=False)
    login: str
    hashed_password: str
    JWT: str = ""


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширование пароля"""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @staticmethod
    def registration(login, password):
        """Регистрация пользователя"""
        if next((user for user in users if user.login == login), None):
            return USER_EXISTS.format(login=login)
        hashed_password = AuthService.hash_password(password)
        user = User(login=login, hashed_password=hashed_password)
        user.JWT = AuthService.generate_jwt_token(user.id)
        users.append(user)
        return user.JWT

    @staticmethod
    def authentication(login: str, password: str) -> str | None:
        """Аутентификация пользователя"""
        user = next((user for user in users if user.login == login), None)
        if user and AuthService.check_password(password, user.hashed_password):
            user.JWT = AuthService.generate_jwt_token(user.id)
            return user.JWT
        return None

    @staticmethod
    def generate_jwt_token(id: int) -> str:
        """Генерация JWT токена"""
        payload = {
            "id": id,
            "exp": (datetime.now() + timedelta(days=1)).timestamp(),
        }
        token = jwt.encode(
            payload, config.SECRET.get_secret_value(), algorithm="HS256"
        )
        return token

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Декодирование JWT токена"""
        try:
            payload = jwt.decode(
                token, config.SECRET.get_secret_value(), algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError(INVALID_TOKEN)
