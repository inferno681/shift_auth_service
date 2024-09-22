from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Abstract base class for tables in db."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """Table names from class names."""
        return cls.__name__.lower()
