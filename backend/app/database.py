"""Async SQLAlchemy engine and session dependencies."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a database session for FastAPI dependencies."""
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a database session for background tasks."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all ORM tables for local development."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)