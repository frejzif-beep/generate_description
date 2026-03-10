import pytest

def test_update_description(client, sample_sneakers_data):
    """Тест: редактирование сгенерированного описания"""
    generate_response = client.post("/api/generate", json=sample_sneakers_data)
    generated_id = generate_response.json()["id"]
    
    update_data = {"edited_text": "Отредактированный текст"}
    response = client.put(f"/api/generate/{generated_id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["generated_text"] == "Отредактированный текст"
    
    
def test_delete_description(client, sample_smartphone_data):
    """Тест: удаление записи по ID"""
    generate_response = client.post("/api/generate", json=sample_smartphone_data)
    generated_id = generate_response.json()["id"]
    
    response = client.delete(f"/api/generate/{generated_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/api/generate/{generated_id}")
    assert get_response.status_code == 404
    
    
def test_delete_not_found(client):
    """Тест: удаление несуществующей записи"""
    response = client.delete("/api/generate/999")
    assert response.status_code == 404
    
