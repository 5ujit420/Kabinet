from operator import or_

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.books.schema import BookIn, BookInfo, BookOut, QueryIn
from app.core.types import ReadingStatus
from app.models.books import Book
from app.models.users import UserBook


class DuplicateEntryException(Exception):
    pass


class NotFoundExepction(Exception):
    pass


async def create(
    db: AsyncSession,
    user_id: UUID4,
    book_info: BookIn,
) -> BookOut:
    async with db.begin():
        book = await db.scalar(
            select(
                Book,
            ).where(
                Book.title == book_info.title,
                Book.author == book_info.author,
            )
        )
        if book is None:
            book = Book(
                title=book_info.title,
                author=book_info.author,
            )
            db.add(book)
            await db.flush()
        existing = await db.scalar(
            select(
                UserBook.id,
            ).where(
                UserBook.book_id == book.id,
                UserBook.user_id == user_id,
            )
        )
        if existing is not None:
            raise DuplicateEntryException
        user_book = UserBook(
            book_id=book.id,
            user_id=user_id,
            reading_status=book_info.reading_status,
        )
        db.add(user_book)
        await db.flush()
    await db.refresh(user_book)
    return BookOut(
        id=user_book.id,
        book=BookInfo.model_validate(book),
        reading_status=user_book.reading_status,
        added_at=user_book.added_at,
    )


async def read(
    db: AsyncSession,
    user_id: UUID4,
    book_id: UUID4,
):
    user_book = await db.scalar(
        select(
            UserBook,
        )
        .join(UserBook.book)
        .options(
            selectinload(UserBook.book),
        )
        .where(
            UserBook.user_id == user_id,
            UserBook.book_id == book_id,
        )
    )
    if user_book is None:
        raise NotFoundExepction
    return BookOut(
        id=user_book.id,
        book=BookInfo.model_validate(user_book.book),
        reading_status=user_book.reading_status,
        added_at=user_book.added_at,
    )


async def update(
    db: AsyncSession,
    user_id: UUID4,
    book_id: UUID4,
    new_reading_status: ReadingStatus,
):
    async with db.begin():
        user_book = await db.scalar(
            select(
                UserBook,
            )
            .join(UserBook.book)
            .options(
                selectinload(UserBook.book),
            )
            .where(
                UserBook.user_id == user_id,
                UserBook.book_id == book_id,
            )
        )
        if user_book is None:
            raise NotFoundExepction
        user_book.reading_status = new_reading_status
    await db.refresh(user_book)
    return BookOut(
        id=user_book.book_id,
        book=BookInfo.model_validate(user_book.book),
        reading_status=user_book.reading_status,
        added_at=user_book.added_at,
    )


async def delete(
    db: AsyncSession,
    user_id: UUID4,
    book_id: UUID4,
):
    async with db.begin():
        user_book = await db.scalar(
            select(
                UserBook,
            )
            .join(UserBook.book)
            .options(
                selectinload(UserBook.book),
            )
            .where(
                UserBook.user_id == user_id,
                UserBook.book_id == book_id,
            )
        )
        if user_book is None:
            raise NotFoundExepction
        await db.delete(user_book)
    return BookOut(
        id=user_book.book_id,
        book=BookInfo.model_validate(user_book.book),
        reading_status=user_book.reading_status,
        added_at=user_book.added_at,
    )


async def read_all(
    db: AsyncSession,
    user_id: UUID4,
    query: QueryIn,
):
    result = await db.scalars(
        select(
            UserBook,
        )
        .join(UserBook.book)
        .options(
            selectinload(UserBook.book),
        )
        .where(
            UserBook.user_id == user_id,
            or_(
                Book.title.ilike(f"%{query.search}%"),
                Book.author.ilike(f"%{query.search}%"),
            ),
        )
        .limit(query.limit)
        .offset(query.offset)
    )
    books = [
        BookOut(
            id=user_book.book_id,
            book=BookInfo.model_validate(user_book.book),
            reading_status=user_book.reading_status,
            added_at=user_book.added_at,
        )
        for user_book in result
    ]
    return books
