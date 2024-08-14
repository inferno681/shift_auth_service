import os
from uuid import uuid1

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemes import (
    IsReady,
    KafkaResponse,
    UserCreate,
    UserToken,
    UserTokenCheck,
    UserTokenCheckRequest,
)
from app.constants import UPLOAD_ERROR, WRONG_IMAGE_FORMAT
from app.service import AuthService, producer
from config import config

router_auth = APIRouter()
router_check = APIRouter()
router_healthz = APIRouter()
router_verify = APIRouter()


@router_auth.post('/registration', response_model=UserToken)
async def registration(user: UserCreate):
    """Эндпоинт регистрации пользователя."""
    return UserToken(
        token=AuthService.registration(
            login=user.login,
            password=user.password,
        ),
    )


@router_auth.post('/auth', response_model=UserToken)
async def authentication(user: UserCreate):
    """Эндпоинт аутентификации пользователя."""
    return UserToken(
        token=AuthService.authentication(
            login=user.login,
            password=user.password,
        ),
    )


@router_check.post('/check_token', response_model=UserTokenCheck)
async def check_token(token: UserTokenCheckRequest):
    """Эндпоинт проверки токена пользователя."""
    return AuthService.check_token(token.token)


@router_healthz.get('/healthz/ready', response_model=IsReady)
async def check_health():
    """Эндпоинт проверки запущен ли сервис."""
    return IsReady(is_ready=True)


@router_verify.post('/verify', response_model=KafkaResponse)
async def verify(user_id: int = Form(gt=0), file: UploadFile = File()):
    """Эндпоинт для загрузки фото."""
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension not in config.service.acceptable_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=WRONG_IMAGE_FORMAT.format(extension=file_extension),
        )
    file_path = f'{config.service.photo_directory}/{uuid1()}{file_extension}'
    try:
        async with aiofiles.open(file_path, 'wb') as photo:
            await photo.write(await file.read())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=UPLOAD_ERROR,
        )
    await producer.send_message('faces', {user_id: file_path})
    AuthService.verify(user_id)
    return KafkaResponse
