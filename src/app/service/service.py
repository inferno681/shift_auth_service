from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.constants import (
    ENCODING_FORMAT,
    INVALID_TOKEN_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
    USER_EXISTS_MESSAGE,
    USER_NOT_FOUND,
)
from app.db import User
from config import config


class TokenService:
    """Token service."""

    @staticmethod
    async def get_token(user_id: int, redis: Redis) -> str | None:
        """Get token from redis."""
        return await redis.get(str(user_id))

    @staticmethod
    async def create_and_put_token(user_id: int, redis: Redis) -> str:
        """Token creation and sending to redis."""
        token = AuthService.generate_jwt_token(user_id)
        await redis.set(user_id, token, config.service.token_ttl)  # type: ignore # noqa: E501
        return token

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check token expiration."""
        try:
            AuthService.decode_jwt_token(token)
        except jwt.ExpiredSignatureError:
            return True
        return False

    @staticmethod
    async def update_token(user_id: int, redis: Redis) -> str:
        """Token update in redis."""
        token = AuthService.generate_jwt_token(user_id)
        await redis.set(user_id, token, config.service.token_ttl)  # type: ignore # noqa: E501
        return token

    @staticmethod
    async def check_token(token: str, redis: Redis) -> dict:
        """Token check method."""
        response = {'user_id': None, 'is_token_valid': False}
        try:
            user_id = AuthService.decode_jwt_token(token)['id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as exeption:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exeption),
            )
        if user_id and token == await TokenService.get_token(user_id, redis):
            response['user_id'] = user_id
            response['is_token_valid'] = True
        return response

    @staticmethod
    def generate_jwt_token(user_id: int) -> str:
        """Token generation."""
        payload = {
            'id': user_id,
            'exp': (
                datetime.now() + timedelta(seconds=config.service.token_ttl)  # type: ignore # noqa: E501
            ).timestamp(),
        }
        return jwt.encode(
            payload,
            config.SECRET.get_secret_value(),  # type: ignore
            algorithm='HS256',
        )

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Token decoding."""
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
    """Auth service."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Password hashing."""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(ENCODING_FORMAT), salt)
        return hashed_password.decode(ENCODING_FORMAT)

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Password check."""
        return bcrypt.checkpw(
            password.encode(ENCODING_FORMAT),
            hashed_password.encode(ENCODING_FORMAT),
        )

    @staticmethod
    async def registration(
        login: str,
        password: str,
        session: AsyncSession,
        redis: Redis,
    ) -> str:
        """User registration."""
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
        await session.commit()
        await session.refresh(user)
        token = AuthService.generate_jwt_token(user.id)
        await redis.set(user.id, token, config.service.token_ttl)  # type: ignore # noqa: E501
        return token

    @staticmethod
    async def get_user(
        login: str,
        password: str,
        session: AsyncSession,
    ) -> User:
        """Get user from db."""
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
        redis: Redis,
    ) -> str | None:
        """User authentication."""
        user = await AuthService.get_user(login, password, session)
        user_id = user.id
        token = await TokenService.get_token(user_id, redis)
        if not token:
            return await TokenService.create_and_put_token(user_id, redis)
        if TokenService.is_token_expired(token):
            return await TokenService.update_token(user_id, redis)
        return token

    @staticmethod
    async def verify(user_id: int, session: AsyncSession):
        """User verification in db."""
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
