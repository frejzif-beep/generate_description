import pytest
from fastapi.testclient import TestClient
from main import app
import os

@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента в FastAPI
    """
    with TestClient(app) as test_client:
        yield test_client
        



@pytest.fixture
def sample_smartphone_data():
    """
    Фикстура с тестовыми данными для смартфона.
    Чтобы не писать одни и те же данные в каждом тесте.
    """
    return {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "model": "iPhone 15",
            "memory": 128,
            "camera": "48 МП"
        }
    }


@pytest.fixture
def sample_sneakers_data():
    """
    Фикстура с тестовыми данными для кроссовок.
    """
    return {
        "category": "sneakers",
        "attributes": {
            "brand": "Nike",
            "model": "Air Force 1",
            "size": 42,
            "color": "White",
            "material": "Leather",
            "color": "White"
        }
    }
    
 
 
 
#ФИКСТУРЫ ДЛЯ ВАЛИДАЦИИ   
@pytest.fixture
def invalid_missing_brand():
    """Данные с отсутствующем брендом"""
    return {
        "category": "smartphones",
        "attributes": {
            "model": "iPhone 15",
            "memory": 128
        }
    }
    

@pytest.fixture
def invalid_missing_model():
    """Данные с отсутствующей моделью"""
    return {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "memory": 128
        }
    }


@pytest.fixture
def invalid_memory_negative():
    """Данные с отрицательной памятью"""
    return {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "model": "iPhone 15",
            "memory": -100
        }
    }


@pytest.fixture
def invalid_memory_too_large():
    """Данные с нереально большой памятью"""
    return {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "model": "iPhone 15",
            "memory": 999999
        }
    }


@pytest.fixture
def invalid_size_negative():
    """Данные с отрицательным размером обуви"""
    return {
        "category": "sneakers",
        "attributes": {
            "brand": "Nike",
            "model": "Air Force 1",
            "size": -10,
            "color": "White"
        }
    }


@pytest.fixture
def invalid_size_too_large():
    """Данные с нереально большим размером обуви"""
    return {
        "category": "sneakers",
        "attributes": {
            "brand": "Nike",
            "model": "Air Force 1",
            "size": 200,
            "color": "White"
        }
    }


@pytest.fixture
def invalid_wrong_category():
    """Данные с несуществующей категорией"""
    return {
        "category": "wrong_category_123",
        "attributes": {
            "brand": "Test",
            "model": "Test Model"
        }
    }


@pytest.fixture
def invalid_empty_attributes():
    """Данные с пустыми атрибутами"""
    return {
        "category": "smartphones",
        "attributes": {}
    }