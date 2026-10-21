from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.core.db import DBSession
from app.core.rate_limiter import limiter
from app.core.types import ReadingStatus
from app.users.services import CurrentUser

from .schema import BookIn, BookOut, QueryIn
from .services import (
    DuplicateEntryException,
    NotFoundExepction,
    create,
    delete,
    read,
    read_all,
    update,
)

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.post(
    "/",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
async def add_book(
    request: Request,
    payload: BookIn,
    db: DBSession,
    user: CurrentUser,
):
    try:
        user_book = await create(db, user, payload)
    except DuplicateEntryException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book Already Exists",
        )
    return user_book


@router.get(
    "/{book_id}",
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("100/minute")
async def get_book(
    request: Request,
    db: DBSession,
    book_id: UUID,
    user: CurrentUser,
):
    try:
        book = await read(db, user, book_id)
    except NotFoundExepction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.patch(
    "/{book_id}",
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("20/minute")
async def update_book(
    request: Request,
    db: DBSession,
    user: CurrentUser,
    book_id: UUID,
    new_reading_status: ReadingStatus,
):
    try:
        book = await update(db, user, book_id, new_reading_status)
    except NotFoundExepction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.delete(
    "/{book_id}",
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def remove_book(
    request: Request,
    db: DBSession,
    user: CurrentUser,
    book_id: UUID,
):
    try:
        book = await delete(db, user, book_id)
    except NotFoundExepction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.get(
    "/",
    response_model=list[BookOut],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("100/minute")
async def get_books(
    request: Request,
    db: DBSession,
    user: CurrentUser,
    query: Annotated[QueryIn, Query()],
):
    return await read_all(db, user, query)
