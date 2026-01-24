from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.SQLALCHEMY_ASYNC_DATABASE_URI,
    poolclass=NullPool,
    future=True,
    echo=settings.SQLALCHEMY_ENABLE_ECHO,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

sync_engine = create_engine(settings.construct_sync_uri())
Session = sessionmaker(bind=sync_engine)


async def get_db() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()


AsyncDBSession = Annotated[AsyncSession, Depends(get_db)]
