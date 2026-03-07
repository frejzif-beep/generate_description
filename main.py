from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.config import settings
from src.db.database import engine, Base 
from src.api.endpoints import generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("Запуск приложения...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("База данных подключена")

    except Exception as e:
        print(f"Ошибка подключения к базу данных: {e}")
        raise
    
    yield
    
    print("Остановка...")
    await engine.dispose()
    print("Соединения закрыты!")
    
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Генератор описаний товаров",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.include_router(generate.router)