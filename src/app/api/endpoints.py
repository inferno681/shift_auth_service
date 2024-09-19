import os
from uuid import uuid1

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from opentracing import global_tracer
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
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт регистрации пользователя."""
    with global_tracer().start_active_span('register_user') as scope:
        scope.span.set_tag('login', user.login)
        return UserToken(
            token=await AuthService.registration(
                login=user.login,
                password=user.password,
                session=session,
                redis=request.app.state.redis,
            ),
        )


@router_auth.post('/auth', response_model=UserToken)
async def authentication(
    user: UserCreate,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """Эндпоинт аутентификации пользователя."""
    with global_tracer().start_active_span('login_user') as scope:
        scope.span.set_tag('login', user.login)
        return UserToken(
            token=await AuthService.authentication(
                login=user.login,
                password=user.password,
                session=session,
                redis=request.app.state.redis,
            ),
        )


@router_check.post('/check_token', response_model=UserTokenCheck)
async def check_token(
    token: UserTokenCheckRequest,
    request: Request,
):
    """Эндпоинт проверки токена пользователя."""
    with global_tracer().start_active_span('check_token') as scope:
        scope.span.set_tag('token', token.token[:10] + '...')
        return await AuthService.check_token(
            token.token,
            request.app.state.redis,
        )


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
    with global_tracer().start_active_span('photo_upload') as scope:
        if file.filename is None:
            scope.span.set_tag('error', FILENAME_ERROR)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILENAME_ERROR,
            )
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension not in config.service.acceptable_formats:  # type: ignore # noqa: E501
            scope.span.set_tag('error', 'wrong file format')
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
            scope.span.set_tag('error', UPLOAD_ERROR)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=UPLOAD_ERROR,
            )
        scope.span.set_tag('file path', file_path)
        await producer.send_message(
            config.service.kafka_topic,  # type: ignore
            {user_id: file_path},
        )
        await AuthService.verify(user_id, session)
        return KafkaResponse
