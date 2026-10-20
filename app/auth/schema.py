from pydantic import BaseModel, EmailStr


class UserForm(BaseModel):
    username: str
    email: EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
