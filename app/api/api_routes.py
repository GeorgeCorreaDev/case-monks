from fastapi import APIRouter, HTTPException, Header, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional

from agent_logic import ask_agent
from core import monks_base_error, scope_error, settings


router = APIRouter()


class _ask_request(BaseModel):
    question: str = Field(
        min_length=5,
        description="pergunta em linguagem natural sobre midia/trafego",
        json_schema_extra={"example": "qual canal trouxe mais receita em 2024?"},
    )
    thread_id: Optional[str] = Field(
        default="default-session",
        description="ID da conversa para manter memoria"
    )


class _ask_response(BaseModel):
    answer: str
    usage: dict = Field(default_factory=dict, description="apuração de tokens e custo")
    resilience: str = Field(default="success", description="status do protocolo de resiliencia")
    status: str = "ok"


class _health_response(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"


API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
# valida se a chave bate com o .env (seguranca basica rs)
    if api_key != settings.api_key_internal:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Chave de API invalida ou ausente.",
        )
    return api_key


@router.get("/health", response_model=_health_response, tags=["infra"])
async def health_check():
    # liveness check | k8s, docker, etc
    return _health_response()


@router.post("/ask", response_model=_ask_response, tags=["agent"])
async def ask_endpoint(
    req: _ask_request,
    _auth: str = Depends(verify_api_key)
):
    # recebe o json e chama o estagiario ou jefrey ..
    try:
        # o ask_agent ja lida com o callback de tokens e resiliencia
        result = await ask_agent(req.question, thread_id=req.thread_id)
        return _ask_response(
            answer=result["answer"],
            usage=result["usage"],
            resilience=result["resilience"]
        )

    except scope_error as e:
        raise HTTPException(status_code=422, detail=e.message) from e

    except monks_base_error as e:
        # caso o estagiario sair mais cedo ou falhar, a gente trata aqui
        # nao surta!!! kkkk
        raise HTTPException(
            status_code=500,
            detail=f"erro interno: {e.message}",
        ) from e

    except Exception as e:
        #  me perdi no caminho!
        raise HTTPException(
            status_code=500,
            detail="erro nao tratado .. ve os logs",
        ) from e
