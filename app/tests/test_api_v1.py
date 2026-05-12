import pytest
from unittest.mock import patch

def test_health_check(client):
    # verifica se o endpoint se health ok
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}

def test_ask_endpoint_success(client):
    # simula pergunta de sucess p/ o agente
    mock_result = {
        "answer": "O canal Google Ads trouxe o maior ROI.",
        "usage": {"total_tokens": 150, "total_cost": 0.002},
        "resilience": "success"
    }
    
    with patch("api.api_routes.ask_agent", return_value=mock_result):
        response = client.post(
            "/api/v1/ask",
            json={"question": "qual canal trouxe mais receita em 2024?"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "O canal Google Ads trouxe o maior ROI."
    assert data["status"] == "ok"

def test_ask_endpoint_validation_error(client):
    # verifica perguntas muito curtas ja rejeitada
    response = client.post(
        "/api/v1/ask",
        json={"question": "oi"}
    )
    assert response.status_code == 422 # pydantic valida erro
