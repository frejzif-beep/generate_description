from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.config import settings
from src.db.database import engine, Base 
from src.api.endpoints import generate
from src.core.logging_config import setup_logging

logger = setup_logging(log_level=settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных подключена")

    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("Остановка...")
    await engine.dispose()
    logger.info("Соединения закрыты!")
    
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Генератор описаний товаров",
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.include_router(generate.router)