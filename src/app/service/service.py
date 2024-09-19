from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.constants import (
    ENCODING_FORMAT,
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
    USER_NOT_FOUND,
)
from app.db import Token, User
from config import config


class TokenService:
    """Сервис работы с токеном."""

    @staticmethod
    async def get_token(user_id: int, session: AsyncSession) -> str | None:
        """Проверка наличия токена пользователя."""
        token = await session.execute(
            select(Token.token).where(Token.user_id == user_id),
        )
        return token.scalar_one_or_none()

    @staticmethod
    async def create_and_put_token(user_id: int, session: AsyncSession) -> str:
        """Создание и отправка токена в хранилище."""
        token = AuthService.generate_jwt_token(user_id)
        session.add(Token(user_id=user_id, token=token))
        await session.commit()
        return token

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Проверка срока действия токена."""
        try:
            AuthService.decode_jwt_token(token)
        except jwt.ExpiredSignatureError:
            return True
        return False

    @staticmethod
    async def update_token(user_id: int, session: AsyncSession) -> str:
        """Обновление существующего токена в хранилище."""
        token = AuthService.generate_jwt_token(user_id)
        Token(user_id=user_id, token=token)
        await session.commit()
        return token

    @staticmethod
    async def check_token(token: str, session: AsyncSession) -> dict:
        """Проверка токена."""
        response = {'user_id': None, 'is_token_valid': False}
        try:
            user_id = AuthService.decode_jwt_token(token)['id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as exeption:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exeption),
            )
        if user_id and token == await TokenService.get_token(user_id, session):
            response['user_id'] = user_id
            response['is_token_valid'] = True
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
    async def registration(
        login: str,
        password: str,
        session: AsyncSession,
    ) -> str:
        """Регистрация пользователя."""
        query_result = await session.execute(
            select(User).where(User.login == login),
        )
        if query_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USER_EXISTS_MESSAGE.format(login=login),
            )
        hashed_password = AuthService.hash_password(password)
        user = User(login=login, hashed_password=hashed_password)
        session.add(user)
        await session.flush()
        token = AuthService.generate_jwt_token(user.id)
        session.add(Token(user_id=user.id, token=token))
        await session.commit()
        return token

    @staticmethod
    async def get_user(
        login: str,
        password: str,
        session: AsyncSession,
    ) -> User:
        """Проверка наличия пользователя в бд."""
        query_result = await session.execute(
            select(User).where(User.login == login),
        )
        user = query_result.scalar_one_or_none()
        if user and AuthService.check_password(password, user.hashed_password):
            return user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND,
        )

    @staticmethod
    async def authentication(
        login: str,
        password: str,
        session: AsyncSession,
    ) -> str | None:
        """Аутентификация пользователя."""
        user = await AuthService.get_user(login, password, session)
        user_id = user.id
        token = await TokenService.get_token(user_id, session)
        if not token:
            return await TokenService.create_and_put_token(user_id, session)
        if TokenService.is_token_expired(token):
            return await TokenService.update_token(user_id, session)
        return token

    @staticmethod
    async def verify(user_id: int, session: AsyncSession):
        """Верификация пользователя в хранилище."""
        query_result = await session.execute(
            select(User).where(User.id == user_id),
        )
        user = query_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )
        user.is_verified = True
        await session.commit()
