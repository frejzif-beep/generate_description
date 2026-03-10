import pytest


def test_get_history(client):
    """Тест: получение истории генерации с пагинацией"""
    response = client.get("/api/history?page=0&size=10")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert isinstance(result["items"], list)
    

def test_get_description_by_id(client, sample_smartphone_data):
    """Тест: получение одной записи по ID"""
    generate_response = client.post("/api/generate", json=sample_smartphone_data)
    generated_id = generate_response.json()["id"]
    
    response = client.get(f"/api/generate/{generated_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == generated_id
    assert "iPhone 15" in result["generated_text"]
    

def test_get_description_not_found(client):
    """Тест: запись по ID не найдена"""
    response = client.get("/api/generate/999")
    assert response.status_code == 404
    
