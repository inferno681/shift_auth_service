from typing import Annotated

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import (
    BALANCE_DEFAULT_VALUE,
    HASHED_PASSWORD_LENGTH,
    LOGIN_LENGTH,
    TOKEN_LENGTH,
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
    token: Mapped['Token'] = relationship(back_populates='user')


class Token(Base):
    """Модель для хранения токена."""

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
    )
    token: Mapped[str | None] = mapped_column(String(TOKEN_LENGTH))
    user: Mapped['User'] = relationship(back_populates='token')
    __table_args__ = (UniqueConstraint('user_id'),)
