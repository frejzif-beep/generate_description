from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Union, Literal
from datetime import date



class BaseAttributes(BaseModel):
    """Общие атрибуты для всех товаров"""
    brand: str = Field(..., min_length=1, max_length=100, description="Бренд")
    
    class Config:
        extra = "forbid"
        
        
class SmartphoneAttributes(BaseAttributes):
    """Атрибуты для смартфонов"""
    model: str = Field(..., min_length=1, max_length=100, description="Модель")
    memory: int = Field(..., ge=4, le=1024, description="ОЗУ")
    camera: Optional[str] = Field(None, description="Камера")
    color: Optional[str] = Field(None, description="Цвет")
    screen_size: Optional[float] = Field(None, ge=3.0, le=20.0, description="Экран")
    
    
class SneakersAttributes(BaseAttributes):
    """Кроссовки"""
    model: str = Field(..., min_length=1, description="Модель")
    size: int = Field(..., ge=30, le=50, description="Размер")
    color: str = Field(..., description="Цвет")
    material: Optional[str] = Field(None, description="Материал")
    
class CoffeeMachineAttributes(BaseAttributes):
    """Кофемашины"""
    model: str = Field(..., min_length=1, description="Модель")
    type: Optional[str] = Field(None, description="Тип")
    power: Optional[str] = Field(None, description="Мощность")
    pressure: Optional[int] = Field(None, ge=1, le=20, description="Давление")
    milk_frother: Optional[bool] = Field(False, description="Капучинатор")
    
    
class LaptopAttributes(BaseAttributes):
    """Ноутбуки"""
    model: str = Field(..., min_length=1, description="Модель")
    memory: int = Field(..., ge=4, le=1024, description="ОЗУ")
    screen: Optional[str] = Field(None, description="Экран")
    processor: Optional[str] = Field(None, description="Процессор")
    weight: Optional[float] = Field(None, ge=0.5, le=5.0, description="Вес")
    

class HeadphonesAttributes(BaseAttributes): 
    """Наушники"""
    model: str = Field(..., min_length=1, description="Модель")
    type: Optional[str] = Field(None, description="Тип")
    battery: Optional[int] = Field(None, ge=1, le=100, description="Время работы (часы)")
    noise_cancelling: Optional[bool] = Field(False, description="Шумоподавление")
    connectivity: Optional[str] = Field(None, description="Подключение")
    driver_size: Optional[str] = Field(None, description="Размер драйвера")


CATEGORY_SCHEMAS ={
    "smartphones": SmartphoneAttributes,
    "sneakers": SneakersAttributes,
    "coffee_machines": CoffeeMachineAttributes,
    "laptops": LaptopAttributes,
    "headphones": HeadphonesAttributes
}