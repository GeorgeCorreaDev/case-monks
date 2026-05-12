from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from pathlib import Path

from langchain_community.callbacks import get_openai_callback
from tenacity import retry, stop_after_attempt, wait_exponential

from core import settings, agent_logic_error
from agent_logic.tools import ALL_TOOLS


# checkpointer em memoria pro agente lembrar da ideia e evita o auzaimer, pause ladainha rsrsr
_memory = MemorySaver()


def _load_brain() -> str:
    # carrega as amarras e habilidades dedicadas do agente
    # essas estao dentro de /app e sao exclusivas pro cerebro da ia 
    # obs!(não vazam pro llm, evitando alucinações e mantendo o foco)
    app_root = Path(__file__).parent.parent
    rules_path = app_root / ".cursorrules"
    skill_path = app_root / "skill.md"

    try:
        rules_text = rules_path.read_text(encoding="utf-8")
        skill_text = skill_path.read_text(encoding="utf-8")
        return f"{rules_text}\n\n{skill_text}"
    except Exception:
        # fallback minimal 
        return "voce é um analista junior de midia da monks. use as ferramentas."


def _get_llm():
    # factory do llm| troca provider via env
    provider = settings.llm_provider.lower()

    if provider == "openai":
        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=0.1,
        )
    
    if provider == "anthropic":
        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            temperature=0.1,
        )
        
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            api_key=settings.google_api_key,
            temperature=0.1,
        )

    raise agent_logic_error(f"provider '{provider}' nao suportado ainda")


def create_agent():
    # monta o grafo do langgraph com checkpointer de memoria
    llm = _get_llm()

    # liga as tools no llm| o react agent faz o loop sozinho
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SystemMessage(content=_load_brain()),
        checkpointer=_memory
    )
    return agent


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def _invoke_agent_with_retry(agent, inputs: dict, config: dict):
    # wrapper com protocolo de resiliencia obs!(retries exponenciais)
    return await agent.ainvoke(inputs, config=config)


async def ask_agent(question: str, thread_id: str = "default-session"):
  # interface principal .. recebe pergunta e retorna resposta + metadados de tokens
    try:
        agent = create_agent()
        config = {"configurable": {"thread_id": thread_id}}
        
        with get_openai_callback() as cb:
            # protocolo de resiliencia> tentamos o melhor, se cair a gente levanta. rsrsr
            result = await _invoke_agent_with_retry(
                agent, 
                {"messages": [("user", question)]},
                config=config
            )
            
            # apuraçao de tokens e custo obs!(pro dono nao levar susto na fatura kkkk)
            usage = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": cb.total_cost,
            }
            
            # trava de segurança: se o custo estourou
            if cb.total_cost > settings.max_token_cost:
                # logamos o estouro internamente
                resilience_status = f"cost_limit_exceeded (investiu ${cb.total_cost:.4f})"
            else:
                resilience_status = "success"
                if cb.successful_requests > 1:
                    resilience_status = "success after retries (estava instavel mas venci! kkkk)"

            return {
                "answer": result["messages"][-1].content,
                "usage": usage,
                "resilience": resilience_status
            }

    except Exception as e:
        # se tudo vai mal, deixa recado no bloco de notas ,, so que nao! rs ;)
        raise agent_logic_error(
            f"ih, deu ruim no ciclo do agente (resiliencia esgotada): {e}",
            {"question": question},
        ) from e
