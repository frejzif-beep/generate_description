from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_generate_smartphone(client, sample_smartphone_data):
    """Тест генерации описания для смартфона"""
    response = client.post("/api/generate", json=sample_smartphone_data)
    result = response.json()
    assert "generated_text" in result
    assert "Apple" in result["generated_text"]
    assert "iPhone 15" in result["generated_text"]
    assert "id" in result
    assert "category" in result
    
    
def test_generate_sneakers(client, sample_sneakers_data):
    """Тест: генерация описания для кроссовок"""
    response = client.post("/api/generate", json=sample_sneakers_data)
    assert response.status_code == 200
    result = response.json()
    assert "generated_text" in result
    assert "Nike" in result["generated_text"]
    assert "Air Force 1" in result["generated_text"]
    
    
def test_generate_wrong_category(client):
    """Тест: ошибка при несуществующей категории"""
    data = {
        "category": "wrong_category_123",
        "attributes": {"brand": "Test", "model": "Test"}
    }
    response = client.post("/api/generate", json=data)
    assert response.status_code == 404
    
    
def test_generate_empty_attributes(client):
    """Тест: ошибка при пустых атрибутах"""
    data = {
        "category": "smartphones",
        "attriutes": {}
    }
    response = client.post("/api/generate", json=data)
    assert response.status_code == 422
    
    
