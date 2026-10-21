import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware

from app.auth import controller as auth
from app.books import controller as books
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import logging_middleware
from app.core.rate_limiter import limiter
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
app.add_middleware(SlowAPIASGIMiddleware)
app.middleware("http")(logging_middleware)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
