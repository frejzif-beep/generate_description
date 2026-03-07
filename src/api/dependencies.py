import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker

logger = logging.getLogger(__name__)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        logger.debug("Сессия БД открыта")
        try:
            yield session
        finally:
            logger.debug("Сессия БД закрыта")