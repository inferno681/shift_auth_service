from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import count

import bcrypt
import jwt

from app.api.schemes import UserTokenCheck
from app.constants import (
    ENCODING_FORMAT,
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
)
from app.service.exceptions import UserExistsError
from config import config

users = []  # type: ignore
tokens = []  # type: ignore
_id_counter = count(1)


@dataclass
class User:
    """Класс пользователя."""

    id: int = field(default_factory=lambda: next(_id_counter), init=False)
    login: str
    hashed_password: str


@dataclass
class Token:
    """Сущность для хранения токена."""

    user_id: int
    token: str


class TokenService:
    """Сервис работы с токеном."""

    @staticmethod
    def get_token(user_id: int) -> str | None:
        """Проверка наличия токена пользователя."""
        return next(
            (token.token for token in tokens if token.user_id == user_id),
            None,
        )

    @staticmethod
    def create_and_put_token(user_id: int) -> str:
        """Создание и отправка токена в хранилище."""
        token = Token(
            user_id=user_id,
            token=AuthService.generate_jwt_token(user_id),
        )
        tokens.append(token)
        return token.token

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Проверка срока действия токена."""
        try:
            AuthService.decode_jwt_token(token)
        except jwt.ExpiredSignatureError:
            return False
        return True

    @staticmethod
    def update_token(user_id: int) -> str:
        """Обновление существующего токена в хранилище."""
        token = next((token for token in tokens if token.user_id == user_id))
        token.token = AuthService.generate_jwt_token(user_id)
        return token.token

    @staticmethod
    def check_token(token: str) -> UserTokenCheck:
        """Проверка токена."""
        response = UserTokenCheck(user_id=None, is_token_valid=False)
        try:
            user_id = AuthService.decode_jwt_token(token)['id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return response
        if user_id and token == TokenService.get_token(user_id):
            response.user_id = user_id
            response.is_token_valid = True
        return response

    @staticmethod
    def generate_jwt_token(user_id: int) -> str:
        """Генерация JWT токена."""
        payload = {
            'id': user_id,
            'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        }
        return jwt.encode(
            payload,
            config.SECRET.get_secret_value(),  # type: ignore
            algorithm='HS256',
        )

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Декодирование JWT токена."""
        try:
            return jwt.decode(
                token,
                config.SECRET.get_secret_value(),  # type: ignore
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(TOKEN_EXPIRED_MESSAGE)
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError(INVALID_TOKEN_MESSAGE)


class AuthService(TokenService):
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
        users.append(user)
        token = AuthService.generate_jwt_token(user.id)
        tokens.append(Token(user.id, token))
        return token

    @staticmethod
    def is_user_exists(login: str, password: str) -> int | None:
        """Проверка наличия пользователя в бд."""
        user = next((user for user in users if user.login == login), None)
        if user and AuthService.check_password(password, user.hashed_password):
            return user.id
        return None

    @staticmethod
    def authentication(login: str, password: str) -> str | None:
        """Аутентификация пользователя."""
        user_id = AuthService.is_user_exists(login, password)
        if not user_id:
            return None
        token = TokenService.get_token(user_id)
        if not token:
            return TokenService.create_and_put_token(user_id)
        if TokenService.is_token_expired(token):
            return TokenService.update_token(user_id)
        return token
