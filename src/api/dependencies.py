import logging
from fastapi import Depends
from typing import AsyncGenerator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker

logger = logging.getLogger(__name__)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        logger.debug("Сессия БД открыта")
        try:
            yield session
        except Exception as e:
            logger.error(f"Ошибка в сессии БД: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            logger.debug("Сессия БД закрыта")
            await session.close()
            
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]