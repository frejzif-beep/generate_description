# src/api/schemas/__init__.py
from .base import (
    ProductGenerateRequest,
    GenerateResponse,
    CategoriesResponse,
    HistoryItem,
    HistoryResponse,
    DeleteResponse,
    ErrorResponse,
    AttributeSchemaResponse,
    UpdateTextRequest
)
from .categories import (
    CATEGORY_SCHEMAS,
    SmartphoneAttributes,
    SneakersAttributes,
    CoffeeMachineAttributes,
    LaptopAttributes,
    HeadphonesAttributes
)

__all__ = [
    # Базовые схемы
    "ProductGenerateRequest",
    "GenerateResponse",
    "CategoriesResponse",
    "HistoryItem",
    "HistoryResponse",
    "DeleteResponse",
    "ErrorResponse",
    "AttributeSchemaResponse",
    "UpdateTextRequest"
    
    # Схемы категорий
    "CATEGORY_SCHEMAS",
    "SmartphoneAttributes",
    "SneakersAttributes",
    "CoffeeMachineAttributes",
    "LaptopAttributes",
    "HeadphonesAttributes"
]