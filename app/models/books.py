from uuid import UUID

from sqlalchemy import String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    users: Mapped[list["UserBook"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Book(id={self.id!r}, "
            f"title={self.title!r}, "
            f"author={self.author!r})"
        )
