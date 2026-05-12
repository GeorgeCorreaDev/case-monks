import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from run import app
from services.bq_service import _bq_service

@pytest.fixture
def client():
    """Fixture para o cliente de testes do FastAPI."""
    return TestClient(app)

@pytest.fixture
def mock_bq_client():
    #simula o client da bigquery .. evitando chamadas reais
    client = MagicMock()
    return client

@pytest.fixture
def bq_service(mock_bq_client):
    # service da big injetado com mock
    service = _bq_service()
    service._client = mock_bq_client
    return service

@pytest.fixture
def mock_llm():
    """Mock do modelo de linguagem (LangChain)."""
    with patch("agent_logic.monks_agent.ChatOpenAI") as mock:
        llm_instance = MagicMock()
        mock.return_value = llm_instance
        yield llm_instance
