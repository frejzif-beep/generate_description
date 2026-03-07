from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any
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
        min_length=1,
        description="Характеристика товара в формате ключ-значение",
        examples = [
            {"brand": "Apple", "model": "iPhone 15", "memory": "128 ГБ"},
            {"brand": "Nike", "model": "Air Force 1", "size": "42"}
        ]
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
        from_attributes=True
    )
    

class HistoryResponse(BaseModel):
    """
    Ответ с историей генераций
    """
    count: int = Field(..., description="Количество записей в ответе")
    items: list[HistoryItem] = Field(..., description="Список записей в истории")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 2,
                "items": [
                    {
                        "id": 1,
                        "category": "smartphones",
                        "generated_text": "Мощный смартфон...",
                        "created_at": "2025-01-15T10:30:00"
                    },
                    {
                        "id": 2,
                        "category": "sneakers",
                        "generated_text": "Стильные кроссовки...",
                        "created_at": "2025-01-15T11:00:00"
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