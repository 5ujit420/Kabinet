import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import controller as auth
from app.books import controller as books
from app.core.config import settings
from app.core.logging import setup_logging
from app.users import controller as users

# from app.core.db import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    # yield
    setup_logging()
    logger.info("Kabinet application starting up")
    yield
    logger.info("Kabinet application shutting down")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
