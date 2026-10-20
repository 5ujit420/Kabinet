from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict

from app.core.types import ReadingStatus


class BookInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    author: str


class BookIn(BaseModel):
    title: str
    author: str
    reading_status: ReadingStatus


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    book: BookInfo
    reading_status: ReadingStatus
    added_at: datetime


class QueryIn(BaseModel):
    offset: int = 0
    limit: int = 10
    search: str | None = None
