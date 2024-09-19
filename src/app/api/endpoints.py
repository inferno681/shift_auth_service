import os
from uuid import uuid1

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemes import (
    IsReady,
    KafkaResponse,
    UserCreate,
    UserToken,
    UserTokenCheck,
    UserTokenCheckRequest,
)
from app.constants import FILENAME_ERROR, UPLOAD_ERROR, WRONG_IMAGE_FORMAT
from app.db import get_async_session
from app.service import AuthService, producer
from config import config

router_auth = APIRouter()
router_check = APIRouter()
router_healthz = APIRouter()
router_verify = APIRouter()


@router_auth.post('/registration', response_model=UserToken)
async def registration(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт регистрации пользователя."""
    return UserToken(
        token=await AuthService.registration(
            login=user.login,
            password=user.password,
            session=session,
        ),
    )


@router_auth.post('/auth', response_model=UserToken)
async def authentication(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт аутентификации пользователя."""
    return UserToken(
        token=await AuthService.authentication(
            login=user.login,
            password=user.password,
            session=session,
        ),
    )


@router_check.post('/check_token', response_model=UserTokenCheck)
async def check_token(
    token: UserTokenCheckRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт проверки токена пользователя."""
    return await AuthService.check_token(token.token, session)


@router_healthz.get('/healthz/ready', response_model=IsReady)
async def check_health():
    """Эндпоинт проверки запущен ли сервис."""
    return IsReady(is_ready=True)


@router_verify.post('/verify', response_model=KafkaResponse)
async def verify(
    user_id: int = Form(gt=0),
    file: UploadFile = File(),
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт для загрузки фото."""
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=FILENAME_ERROR,
        )
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension not in config.service.acceptable_formats:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=WRONG_IMAGE_FORMAT.format(extension=file_extension),
        )
    file_path = (
        f'{config.service.photo_directory}/'  # type: ignore
        f'{uuid1()}{file_extension}'
    )
    try:
        async with aiofiles.open(file_path, 'wb') as photo:
            await photo.write(await file.read())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=UPLOAD_ERROR,
        )
    await producer.send_message(
        config.service.kafka_topic,  # type: ignore
        {user_id: file_path},
    )
    await AuthService.verify(user_id, session)
    return KafkaResponse
