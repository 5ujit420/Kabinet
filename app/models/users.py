from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.types import ReadingStatus


class UserBook(Base):
    __tablename__ = "user_books"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_books_user_id_book_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
    )
    reading_status: Mapped[ReadingStatus] = mapped_column(
        SQLAlchemyEnum(
            ReadingStatus,
            name="reading_status_enum",
            native_enum=False,
            create_constraint=True,
        ),
        default=ReadingStatus.WANT_TO_READ,
        nullable=False,
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="books",
    )
    book: Mapped["Book"] = relationship(
        back_populates="users",
    )

    def __repr__(self) -> str:
        return (
            f"UserBook(user_id={self.user_id!r}, "
            f"book_id={self.book_id!r}, "
            f"reading_status={self.reading_status!r}, "
            f"added_at={self.added_at!r})"
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    books: Mapped[list["UserBook"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, "
            f"username={self.username!r}, "
            f"email={self.email!r}, "
            f"created_at={self.created_at!r})"
        )
