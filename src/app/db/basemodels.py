from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Абстрактный базовый класс для создания таблиц."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """Использование названий таблиц из названий класса."""
        return cls.__name__.lower()
