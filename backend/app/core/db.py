from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

engine = create_async_engine(get_settings().database_url, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    from app.models import Batch, Enquiry, Extraction

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
