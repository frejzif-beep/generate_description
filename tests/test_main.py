from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_generate_smartphone():
    """Тест генерации описания для смартфона"""
    
    data = {
        "category": "smartphones",
        "attributes": {
            "brand": "Apple",
            "model": "iPhone 15",
            "memory": 128,
            "camera": "48 МП"
        }
    }
    response = client.post("/api/generate", json=data)
    
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        print(f"Ответ: {response.json()}")
    
    assert response.status_code == 200
    
    result = response.json()
    assert "generated_text" in result
    assert "Apple" in result["generated_text"]
    assert "iPhone 15" in result["generated_text"]
    assert "id" in result
    assert "category" in result
    
    
def test_generate_empty_attributes():
    """Тест: ошибка при пустых атрибутах"""
    
    data = {
        "category": "smartphone",
        "attributes": {}
    }
    response = client.post("/api/generate", json=data)
    
    assert response.status_code == 422