import pytest

def test_validation_missing_brand(client, invalid_missing_brand):
    """тест: ошибка при отсутствии бренда"""
    response = client.post("/api/generate", json=invalid_missing_brand)
    assert response.status_code == 400
    
    
def test_validation_missing_model(client, invalid_missing_model):
    """Тест: ошибка при отсутствии модели"""
    response = client.post("/api/generate", json=invalid_missing_model)
    assert response.status_code == 400
    
    
def test_validation_memory_negative(client, invalid_memory_negative):
    """Тест: ошибка при отрицательной памяти"""
    response = client.post("/api/generate", json=invalid_memory_negative)
    assert response.status_code == 400
    

def test_validation_memory_too_large(client, invalid_memory_too_large):
    """Тест: ошибка при слишком большой памяти"""
    response = client.post("/api/generate", json=invalid_memory_too_large)
    assert response.status_code == 400


def test_validation_size_negative(client, invalid_size_negative):
    """Тест: ошибка при отрицательном размере"""
    response = client.post("/api/generate", json=invalid_size_negative)
    assert response.status_code == 400
    

def test_validation_size_too_large(client, invalid_size_too_large):
    """Тест: ошибка при слишком большом размере"""
    response = client.post("/api/generate", json=invalid_size_too_large)
    assert response.status_code == 400
    
    
def test_validation_wrong_category(client, invalid_wrong_category):
    """Тест: ошибка при несуществующей категории"""
    response = client.post("/api/generate", json=invalid_wrong_category)
    assert response.status_code == 404
    
    
def test_validation_empty_attributes(client, invalid_empty_attributes):
    """Тест: ошибка при пустых атрибутах"""
    response = client.post("/api/generate", json=invalid_empty_attributes)
    assert response.status_code == 422