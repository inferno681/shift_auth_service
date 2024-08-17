"""Базовые настройки."""

ENCODING_FORMAT = 'utf-8'
LOGIN_LENGTH = 20
BALANCE_DEFAULT_VALUE = 0
HASHED_PASSWORD_LENGTH = 60
TOKEN_LENGTH = 300

"""Сообщения об ошибках."""


INVALID_TOKEN_MESSAGE = 'Недействительный токен'
TOKEN_EXPIRED_MESSAGE = 'Срок действия токена истек'
USER_EXISTS_MESSAGE = 'Пользователь {login} уже существует'
USER_NOT_FOUND = 'Пользователь с предоставлеными данными не найден'
TOKEN_NOT_FOUND = 'Токен отсутствует'
UPLOAD_ERROR = 'Ошибка при загрузке файла'
WRONG_IMAGE_FORMAT = 'Недопустимый формат изображения {extension}'
FILENAME_ERROR = 'Имя файла слищком короткое или файл не имеет расширения'


"""Значения по умолчанию"""
DEFAULT_BALANCE = 500


"""Текст для ответов."""
KAFKA_RESPONSE = 'Сообщение принято в обработку'
