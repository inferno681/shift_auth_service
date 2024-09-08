from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import (
    BALANCE_DEFAULT_VALUE,
    HASHED_PASSWORD_LENGTH,
    LOGIN_LENGTH,
)
from app.db.basemodels import Base

intpk = Annotated[int, mapped_column(primary_key=True)]


class User(Base):
    """Модель пользователя."""

    id: Mapped[intpk]
    login: Mapped[str] = mapped_column(String(LOGIN_LENGTH), unique=True)
    hashed_password: Mapped[str] = mapped_column(
        String(HASHED_PASSWORD_LENGTH),
    )
    balance: Mapped[int] = mapped_column(default=BALANCE_DEFAULT_VALUE)
    is_verified: Mapped[bool] = mapped_column(default=False)
