from __future__ import annotations

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from services import bq


# schemas de entrada | pydantic v2 p/ validar + desc pro llm
class _date_range_input(BaseModel):
    start_date: str = Field(description="data inicio formato yyyy-mm-dd")
    end_date: str = Field(description="data fim formato yyyy-mm-dd")


class _channel_input(BaseModel):
    channel: str = Field(description="canal de trafego: search, organic, facebook, display, email")
    start_date: str = Field(description="data inicio formato yyyy-mm-dd")
    end_date: str = Field(description="data fim formato yyyy-mm-dd")


# tools | mapeiam pros metodos do bq
# o llm decide qual usar pela pergunta

@tool(args_schema=_date_range_input)
def get_revenue_by_channel(start_date: str, end_date: str) -> list[dict]:
    #retorna receita .. pedidos e users unicos agrupados por canal no per informado
    return bq.revenue_by_channel(start_date, end_date)


@tool(args_schema=_date_range_input)
def get_conversion_rate(start_date: str, end_date: str) -> list[dict]:
    # retorna a taxa de conversao <compradores vs visitantes> por canal no periodo info
    return bq.conversion_rate_by_channel(start_date, end_date)


@tool(args_schema=_date_range_input)
def get_ticket_medio(start_date: str, end_date: str) -> list[dict]:
    #retorna o ticket medio das vendas agrupado por canal no perodo info
    return bq.ticket_medio_by_channel(start_date, end_date)


@tool(args_schema=_channel_input)
def get_top_products(channel: str, start_date: str, end_date: str) -> list[dict]:
    #retorna os top 10 produtos mais vend de um canal especifico no periodo info
    return bq.top_products_by_channel(channel, start_date, end_date)


@tool
def get_data_dictionary() -> list[dict]:
    # retorna o dicionário de dados (esquema) das tabelas da big para evitar alucinacoes < > bq rules!
    return bq.get_schema_info()


# lista p/ o agente | se preciso só add new tools aqui
ALL_TOOLS = [
    get_revenue_by_channel,
    get_conversion_rate,
    get_ticket_medio,
    get_top_products,
    get_data_dictionary,
]
