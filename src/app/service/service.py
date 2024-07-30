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
tokens = []
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
    @staticmethod
    def is_token_exists(user_id: int) -> str | None:
        return next(
            (token for token in tokens if token.user_id == user_id),
            None,
        )

    @staticmethod
    def create_and_put_token(user_id: int) -> str:
        token = Token(
            user_id=user_id,
            token=AuthService.generate_jwt_token(user_id),
        )
        return token.token

    @staticmethod
    def is_token_expired(token: str):
        try:
            AuthService.decode_jwt_token(token)
        except jwt.ExpiredSignatureError:
            return False
        return True
    @staticmethod
    def update_token(user_id) -> str:
        token = next(
            (token for token in tokens if token.user_id == user_id),
            None,
        )
        token.token = AuthService.generate_jwt_token(user_id)


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
        users.append(user)
        token = AuthService.generate_jwt_token(user.id)

        tokens.append(user)
        return token

    @staticmethod
    def is_user_exists(login: str, password: str) -> int | None:
        user = next((user for user in users if user.login == login), None)
        if user and AuthService.check_password(password, user.hashed_password):
            return user.id
        return None

    @staticmethod
    def authentication(login: str, password: str) -> str | None:
        """Аутентификация пользователя."""
        user_id = AuthService.is_user_exists(login, password)
        if not user_id:
            raise Exception
        token = TokenService.is_token_exists(user_id)
        if not token:
            return TokenService.create_and_put_token(user_id)
        if TokenService.is_token_expired(token):


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

    @staticmethod
    def check_token(token: str) -> UserTokenCheck:
        """Проверка токена."""
        response = UserTokenCheck(user_id=None, is_token_valid=False)
        try:
            user_id = AuthService.decode_jwt_token(token)['id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return response
        user = next(
            (
                user
                for user in users
                if user.id == user_id and user.token == token
            ),
            None,
        )
        if user:
            response.user_id = user_id
            response.is_token_valid = True
        return response
