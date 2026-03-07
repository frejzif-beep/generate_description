import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from src.api.dependencies import get_async_session
from src.db.models import GeneratedDescription
from src.services.generator import global_generator_service

from src.services.exceptions import (
    GeneratorError,
    TemplateNotFoundError,
    TemplateDataError,
    TemplateFileError
)

from src.api.schemas import (
    ProductGenerateRequest, 
    GenerateResponse,
    HistoryResponse,
    DeleteResponse,
    CategoriesResponse
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_description(
    request: ProductGenerateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Генерируем описание товаров на основе характеристик
    """
    logger.info(f"Запрос на генерацию: category={request.category}, attrs={request.attributes}")
    
    try:
        generated_description_text = global_generator_service.generate(request.category, request.attributes)
        logger.info(f"Генерация успешна: {len(generated_description_text)} символов")
        
    except TemplateNotFoundError as e:
        logger.warning(f"Шаблон не найден: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон для данной категории не найден"
        )
        
    except TemplateDataError as e:
        logger.warning(f"Ошибка данных шаблона: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректные данные для генерации"
        )
        
    except TemplateFileError as e:
        logger.error(f"Ошибка файла шаблона: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
        
    except GeneratorError as e:
        logger.error(f"Ошибка генератора: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при генерации описания"
        )
    
    try:  
        db_result = GeneratedDescription(
            category = request.category,
            product_data = request.attributes,
            generated_text = generated_description_text
        )
    
        db.add(db_result)
        await db.commit()
        await db.refresh(db_result)
        
        logger.info(f"Сохранено в базу данных: id={db_result.id}")
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка базы данных при сохранении: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при созданении в базу данных"
        )
    
    return GenerateResponse(
        id=db_result.id,
        category=db_result.category,
        generated_text=db_result.generated_text
    )


@router.get("/generate/{description_id}", response_model=GenerateResponse)
async def get_description_byId(
    description_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получаем сгенерированное описание по ID
    """
    
    logger.debug(f"Запрос описания: id={description_id}")
    
    try:
        query = select(GeneratedDescription).where(GeneratedDescription.id==description_id)
        result = (await db.execute(query)).scalar_one_or_none()
        
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при получении: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных"
        )

    if not result:
        logger.warning(f"Запись не найдена: id={description_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {description_id} не найдена"
        )
    logger.info(f"Возвращено описание: id={result.id}")
    return GenerateResponse(
        id=result.id,
        category=result.category,
        generated_text=result.generated_text
    )
    
    
@router.delete("/generate/{description_id}", response_model=DeleteResponse)
async def delete_description_byId(
    description_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Запрос на удаление: id={description_id}")
    
    try:
        query = select(GeneratedDescription).where(GeneratedDescription.id == description_id)
        result = (await db.execute(query)).scalar_one_or_none()
        
        if not result:
            logger.warning(f"Запись не найдена для удаления: id={description_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запись с ID {description_id} не найдена"
            )
        
        delete_query = delete(GeneratedDescription).where(GeneratedDescription.id == description_id)
        await db.execute(delete_query)
        await db.commit()
        
        logger.info(f"Удалено: id={description_id}")
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка базы данных при удалении: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении из базы данных"
        )
    
    return DeleteResponse(
        message=f"Запись с ID {description_id} успешно удалена",
        deleted_id=description_id
    )


@router.get(
    "/history",
    response_model=HistoryResponse
)
async def get_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_session)
):
    logger.debug(f"Запрос истории: limit={limit}, offset={offset}")
    
    try:
        query = select(GeneratedDescription).order_by(GeneratedDescription.created_at.desc()).limit(limit).offset(offset)
        result = (await db.execute(query)).scalars().all()
        
        logger.info(f"Возвращено {len(result)} записей")
        
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при получении истории: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории"
        )
    
    return HistoryResponse(
        count = len(result),
        items=result
    )
    

@router.get("/categories")
async def get_categories():
    
    logger.debug("Запрос списка категорий")
    
    categories = list(global_generator_service.templates.keys())
    
    logger.info(f"Возвращено {len(categories)} категорий: {categories}")
    
    return CategoriesResponse(
        count=len(categories),
        categories=categories
    )
