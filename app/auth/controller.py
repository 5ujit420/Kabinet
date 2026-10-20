from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.services import WrongCredentialsException, authenticate_and_create_token
from app.core.db import DBSession

from .schema import TokenOut

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/login",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    try:
        access_token = await authenticate_and_create_token(
            db,
            form_data.username,
            form_data.password,
        )
    except WrongCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenOut(
        access_token=access_token,
        token_type="bearer",
    )
