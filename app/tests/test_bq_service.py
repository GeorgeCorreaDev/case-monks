import pytest
from unittest.mock import MagicMock

def test_get_schema_info_success(bq_service, mock_bq_client):
    # arruma o mock pra retornar um dicionario (como o BQ Row.dict() faria)
    mock_row = {"table_name": "users", "column_name": "traffic_source", "data_type": "STRING"}
    
    mock_query_job = MagicMock()
    mock_query_job.result.return_value = [mock_row]
    mock_bq_client.query.return_value = mock_query_job

    # executa
    schema = bq_service.get_schema_info()

    # valida se o junior não e estagiario e checo as entidades DB
    assert len(schema) == 1
    assert schema[0]["table_name"] == "users"
    mock_bq_client.query.assert_called_once()

def test_bq_execution_error_handling(bq_service, mock_bq_client):
    # simula um err de explosao no big
    mock_bq_client.query.side_effect = Exception("Quota exceeded")

    with pytest.raises(Exception): # classe customizada bq_execution_error
        bq_service.get_schema_info()
