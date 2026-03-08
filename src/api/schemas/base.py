from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime


class ProductGenerateRequest(BaseModel):
    """
    Запрос на генерацию описания товара.
    
    Пример:
    {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "model": "iPhone 15",
            "color": "Black"
        }
    }
    """
    category: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Категория товара (например: smartphone)",
        examples = ["smartphones", "sneakers", "coffee_machines"]                  
    )
    attributes: Dict[str, Any] = Field(
        ...,
        description="Характеристика товара в формате ключ-значение"
    )
    
    
class GenerateResponse(BaseModel):
    """
    Ответ после успешной генерации описания.
    """
    id: int = Field(..., description="Уникальный ID записи в базе")
    category: str = Field(..., description="Категория товара")
    generated_text: str = Field(..., description="Сгенерированное текстовое описание")
    status: str = Field(default="success", description="Статус операции")
    #как пример для Swagger UI
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "category": "smartphones",
                "generated_text": "Мощный Apple iPhone 15 с памятью 128 ГБ...",
                "status": "success"
            }
        }
    )


class UpdateTextRequest(BaseModel):
    """
    Запрос на редактирование сгенерированного текста
    """
    edited_text: str = Field(..., min_length=1, max_length=10000, description="Отредактированный пользователем текст описания")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "edited_text": "Этот мощный Apple iPhone 15 с памятью 128 ГБ - лучший выбор для профессионалов!"
            }
        }
    )


class DeleteResponse(BaseModel):
    """
    Ответ после успешного удаления.
    """
    message: str = Field(..., description="Сообщение об успехе")
    status: str = Field(default="success", description="Статус операции")
    deleted_id: int = Field(..., description="ID удалённой записи")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Запись с ID 1 успешно удалена",
                "status": "success",
                "deleted_id": 1
            }
        }
    )   
    
    
    
class CategoriesResponse(BaseModel):
    """
    Ответ со списками доступных категорий
    """
    count: int = Field(..., description="Количество доступных категорий")
    categories: list[str] = Field(..., description="Список названий категорий")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 5,
                "categories": ["smartphones", "sneakers", "coffee_machines"]
            }
        }
    )


class HistoryItem(BaseModel):
    """
    Элемент истории сгенерированных описаний
    """
    id: int
    category: str
    generated_text: str
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "category": "smartphones",
                "generated_text": "Мощный смартфон...",
                "created_at": "2025-01-15T10:30:00"
            }
        }
    )
    

class HistoryResponse(BaseModel):
    """
    Ответ с историей генераций
    """
    total: int = Field(..., description="Количество записей в ответе")
    page: int = Field(..., description="Текущая страница.")
    size: int = Field(..., description="Размер страницы.")
    pages: int = Field(..., description="Всего страниц.")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")
    items: list[HistoryItem] = Field(..., description="Записи на текущей странице")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "page": 0,
                "size": 10,
                "pages": 10,
                "has_next": True,
                "has_prev": False,
                "items": [
                    {
                        "id": 1,
                        "category": "smartphones",
                        "generated_text": "Мощный смартфон...",
                        "created_at": "2025-01-15T10:30:00"
                    }
                ]
            }
        }
    )
    

class ErrorResponse(BaseModel):
    """
    Стандартный формат ошибка API
    """
    detail: str = Field(..., description="Описание ошибки")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Нужно указать category и attributes"}
        }
    )
    
class AttributeSchemaResponse(BaseModel):
    """Ответ с JSON-схемой атрибутов для категории"""
    category: str = Field(..., description="Категория товара")
    schema: Optional[Dict[str, Any]] = Field(None, description="JSON-схема атрибутов.")
    fields: List[str] = Field(..., description="Список доступных полей")
    required: List[str] = Field(..., description="Список обязательных полей")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "smartphones",
                "schema": {
                    "properties": {
                        "brand": {"type": "string", "description": "Бренд"},
                        "model": {"type": "string", "description": "Модель"}
                    }
                },
                "fields": ["brand", "model", "memory"],
                "required": ["brand", "model"]
            }
        }
    )