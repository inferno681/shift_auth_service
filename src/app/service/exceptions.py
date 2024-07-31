class UserExistsError(Exception):
    """Пользователь уже существует."""


class UserNotExistsError(Exception):
    """Пользователя с предоставлеными данныи не существует."""
