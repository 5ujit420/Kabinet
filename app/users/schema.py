from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field


class UserIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=25)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    username: str
    email: str
    created_at: datetime
