from fastapi import APIRouter, Depends, HTTPException, status
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


router = APIRouter(prefix="/api", tags=["Genaration"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_description(
    request: ProductGenerateRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Генерируем описание товаров на основе характеристик
    """
    try:
        generated_description_text = global_generator_service.generate(request.category, request.attributes)
    
    except TemplateNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ошибка: {str(e)}"
        )
        
    except TemplateDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка: {str(e)}"
        )
        
    except TemplateFileError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка: {str(e)}"
        )
        
    except GeneratorError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка: {str(e)}"
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
        
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
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
    Получаем сгенерированное описние по ID
    """
    try:
        query = select(GeneratedDescription).where(GeneratedDescription.id==description_id)
        result = (await db.execute(query)).scalar_one_or_none()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {result.id} не найдена"
        )
    
    return GenerateResponse(
        id=result.id,
        category=result.category,
        generated_text=result.generated_text
    )
    
    
@router.delete(
    "/generate/{description_id}",
    response_model=DeleteResponse
)
async def delete_description_byId(
    description_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(GeneratedDescription).where(GeneratedDescription.id == description_id)
        result = (await db.execute(query)).scalar_one_or_none
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запись в ID {result.id} не найдена"
            )
        
        delete_query = delete(GeneratedDescription).where(GeneratedDescription.id == description_id)
        await db.execute(delete_query)
        await db.commit()
        
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    
    return DeleteResponse(
        message=f"Запись в ID {description_id} успешно удалена",
        deleted_id=description_id
    )


@router.get(
    "/history",
    response_model=HistoryResponse
)
async def get_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    if limit > 100:
        limit = 100
        
    try:
        query = select(GeneratedDescription).order_by(GeneratedDescription.created_at.desc())
        result = (await db.execute(query)).scalars().all()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    
    return HistoryResponse(
        count = len(result),
        items=result
    )
    

@router.get("/categories")
async def get_categories():
    categories = list(global_generator_service.templates.keys())
    
    return CategoriesResponse(
        count=len(categories),
        categories=categories
    )
