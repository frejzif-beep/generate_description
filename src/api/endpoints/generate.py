import logging
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from src.db.models import GeneratedDescription
from src.services.generator import global_generator_service
from pydantic import ValidationError
from src.api.dependencies import SessionDep
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
    CategoriesResponse,
    AttributeSchemaResponse,
    UpdateTextRequest,
    CATEGORY_SCHEMAS
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_description(
    request: ProductGenerateRequest,
    db: SessionDep
):
    """
    Генерируем описание товаров на основе характеристик
    """
    logger.info(f"Запрос на генерацию: category={request.category}, attrs={request.attributes}")
    
    try:
        if request.category in CATEGORY_SCHEMAS:
            schema_class = CATEGORY_SCHEMAS[request.category]
            validated_attrs = schema_class(**request.attributes)
            attributes_dict = validated_attrs.model_dump(exclude_unset=True)
            logger.info(f"Атрибуты провалидированы для {request.category}")
        else:
            if request.category in global_generator_service.templates:
                attributes_dict = request.attributes
                logger.warning(f"Категории {request.category} есть в шабллонах, но нет схемы валидации")
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория '{request.category}' не поддерживается"
                )
    except ValidationError as e:
        logger.warning(f"Ошибка валидации: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверные атрибуты для категории {request.category}: {str(e)}"
        )
    
    try:
        generated_description_text = global_generator_service.generate(request.category, attributes_dict)
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
            product_data = attributes_dict,
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
            detail="Ошибка при созданении в базе данных"
        )
    
    return GenerateResponse(
        id=db_result.id,
        category=db_result.category,
        generated_text=db_result.generated_text
    )


@router.get("/generate/{description_id}", response_model=GenerateResponse)
async def get_description_byId(
    description_id: int,
    db: SessionDep
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


@router.put("/generate/{description_id}", response_model=GenerateResponse)
async def update_description_by_Id(
    description_id: int,
    request: UpdateTextRequest,
    db: SessionDep
):
    logger.info(f"Запрос на редактирование описания: id={description_id}")
    logger.debug(f"Новый текст (первые 100 символов): {request.edited_text[:100]}...")
    
    try:
        query = select(GeneratedDescription).where(GeneratedDescription.id == description_id)
        result = (await db.execute(query)).scalar_one_or_none()
        
        if not result:
            logger.warning(f"Запись не найдена для редактирования: id={description_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запись с ID {description_id} не найдена"
            )
        old_text = result.generated_text
        result.generated_text = request.edited_text
        
        await db.commit()
        await db.refresh(result)

        logger.debug(f"Длина текста изменилась: {len(old_text)} -> {len(request.edited_text)} символов")
        
        return GenerateResponse(
            id=result.id,
            category=result.category,
            generated_text=result.generated_text            
        )
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка БД при редактировании id={description_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении отредактированного текста"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при редактировании id={description_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
        
        
@router.delete("/generate/{description_id}", response_model=DeleteResponse)
async def delete_description_byId(
    description_id: int,
    db: SessionDep
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
    db: SessionDep,
    page: int = Query(0, ge=0, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы."),
):
    logger.debug(f"Запрос истории: page={page}, size={size}")
    
    try:
        total_query = select(func.count()).select_from(GeneratedDescription)
        total = (await db.execute(total_query)).scalar_one()
        
        query = select(GeneratedDescription).order_by(GeneratedDescription.created_at.desc()).limit(size).offset(size*page)
        result = (await db.execute(query)).scalars().all()
        
        pages = (total + size - 1) // size if total > 0 else 0
        has_next = page + 1 < pages
        has_prev = page > 0
        
        logger.info(f"Возвращено {len(result)}/{total} записей, страница {page}")
        
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при получении истории: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории"
        )
    
    return HistoryResponse(
        total = total,
        page = page,
        size = size,
        pages = pages,
        has_next = has_next,
        has_prev = has_prev,
        items=result
    )
    
    
@router.get("/history/{category}", response_model=HistoryResponse)
async def get_history_by_category(
    category: str,
    db: SessionDep, 
    page: int = Query(0, ge=0, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    """Возвращает историю генераций для конкретной категории"""
    logger.debug(f"Запрос истории для категории {category}: page = {page}, size = {size}")
    
    try:
        if category not in global_generator_service.templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория '{category}' не найдена"
            )

        total_query = select(func.count()).select_from(GeneratedDescription).where(GeneratedDescription.category == category)
        total = (await db.execute(total_query)).scalar_one()
        
        query = (
            select(GeneratedDescription)
            .where(GeneratedDescription.category == category)
            .order_by(GeneratedDescription.created_at.desc())
            .offset(page * size)
            .limit(size)
        )
        
        result = (await db.execute(query)).scalars().all()
        
        pages = (total + size - 1) // size if total > 0 else 0
        
        logger.info(f"Возвращено {len(result)}/{total} записей для {category}")
        
        return HistoryResponse(
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page + 1 < pages,
            has_prev=page > 0,
            items=result
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Ошибка БД: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории"
        )
    
    
@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    logger.debug("Запрос списка категорий")
    categories = list(global_generator_service.templates.keys())
    logger.info(f"Возвращено {len(categories)} категорий: {categories}")
    return CategoriesResponse(
        count=len(categories),
        categories=categories
    )


@router.get("/attributes/{category}", response_model=AttributeSchemaResponse)
async def get_category_attributes(category: str):
    """Возвращает JSON-схему атрибутов для указанной категории"""
    if category in CATEGORY_SCHEMAS:
        model_class = CATEGORY_SCHEMAS[category]
        schema = model_class.model_json_schema()
        
        # Получаем список всех полей
        properties = schema.get("properties", {})
        fields = list(properties.keys())
        
        # Получаем обязательные поля
        required = schema.get("required", [])
        
        return AttributeSchemaResponse(
            category=category,
            schema=schema,
            fields=fields,
            required=required
        )
        
    elif category in global_generator_service.templates:
        return AttributeSchemaResponse(
            category=category,
            schema=None,
            fields=[],
            required=[]
        )
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Категория '{category}' не найдена"
    ) 