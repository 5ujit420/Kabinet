from fastapi import APIRouter, HTTPException, Request, status

from app.core.db import DBSession
from app.core.rate_limiter import limiter

from .schema import UserIn, UserOut
from .services import (
    CredentialsException,
    CurrentUser,
    EmailAlreadyExists,
    UsernameAlreadyExists,
    create_user,
    get_user_data,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
)
@limiter.limit("15/minute")
async def register(
    request: Request,
    payload: UserIn,
    db: DBSession,
) -> UserOut:
    try:
        user = await create_user(payload, db)
    except UsernameAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exist",
        )
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exist",
        )
    return UserOut.model_validate(user)


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("100/minute")
async def get_users(
    request: Request,
    db: DBSession,
    user_id: CurrentUser,
):
    try:
        user_data = await get_user_data(db, user_id)
    except CredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data
