import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from agent_logic.monks_agent import ask_agent
from langchain_core.messages import AIMessage

@pytest.mark.asyncio
async def test_ask_agent_logic_flow(mock_llm):
   
    # test se o fluxo principal do ask_agent ta func com o llm mockado.
    
    mock_agent_instance = MagicMock()
    mock_agent_instance.ainvoke = AsyncMock(return_value={
        "messages": [AIMessage(content="Simulação de resposta do agente.")]
    })
    
    # mock a funçao create_agent para return mock_agent_instance
    with patch("agent_logic.monks_agent.create_agent", return_value=mock_agent_instance):
        with patch("agent_logic.monks_agent.get_openai_callback") as mock_cb:
            cb_instance = MagicMock()
            cb_instance.total_tokens = 100
            cb_instance.prompt_tokens = 50
            cb_instance.completion_tokens = 50
            cb_instance.total_cost = 0.001
            cb_instance.successful_requests = 1
            mock_cb.return_value.__enter__.return_value = cb_instance
            
            result = await ask_agent("qual o ROI de ontem?")
            
            assert "simulaçao" in result["answer"]
            assert result["usage"]["total_tokens"] == 100
            assert result["resilience"] == "success"

@pytest.mark.asyncio
async def test_ask_agent_cost_protection(mock_llm):
    # verifica se o alerta de custo funciona
    mock_agent_instance = MagicMock()
    mock_agent_instance.ainvoke = AsyncMock(return_value={
        "messages": [AIMessage(content="Dando um alerta.")]
    })
    
    with patch("agent_logic.monks_agent.create_agent", return_value=mock_agent_instance):
        with patch("agent_logic.monks_agent.get_openai_callback") as mock_cb:
            cb_instance = MagicMock()
            cb_instance.total_cost = 5.0 # alto custo
            mock_cb.return_value.__enter__.return_value = cb_instance
            
            with patch("agent_logic.monks_agent.settings") as mock_settings:
                mock_settings.max_token_cost = 1.0
                
                result = await ask_agent("query cara")
                assert "cost_limit_exceeded" in result["resilience"]
