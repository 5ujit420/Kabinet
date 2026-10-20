from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import TokenData
from app.auth.services import ALGORITHM, SECRET_KEY, oauth2_scheme
from app.core.db import AuthDBSession
from app.core.utils import get_hashed_password
from app.models.users import User


class UsernameAlreadyExists(Exception):
    pass


class EmailAlreadyExists(Exception):
    pass


class CredentialsException(Exception):
    pass


async def create_user(
    payload,
    db: AsyncSession,
):
    async with db.begin():
        uname_exists = await db.scalar(
            select(
                User.id,
            ).where(
                User.username == payload.username,
            )
        )
        if uname_exists is not None:
            raise UsernameAlreadyExists
        email_exists = await db.scalar(
            select(
                User.id,
            ).where(
                User.email == payload.email,
            )
        )
        if email_exists is not None:
            raise EmailAlreadyExists
        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=get_hashed_password(payload.password),
        )
        db.add(new_user)
        await db.flush()
    await db.refresh(new_user)
    return new_user


async def get_user_data(db: AsyncSession, user_id: UUID4):
    async with db.begin():
        user = await db.scalar(
            select(
                User,
            ).where(
                User.id == user_id,
            )
        )
    return user


async def get_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AuthDBSession,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user_id = await db.scalar(
        select(
            User.id,
        ).where(
            User.username == token_data.username,
        )
    )
    if user_id is None:
        raise credentials_exception
    return user_id


CurrentUser = Annotated[UUID4, Depends(get_user_id)]
