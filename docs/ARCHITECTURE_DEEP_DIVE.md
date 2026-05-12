# Tech Deep Dive

Detalhes de implementação, fluxo de dados e decisões de infra.

## 1. Engine de Orquestração (LangGraph)

Sair de chains lineares pra um Grafo de Estados. Motivos:
- **Auto-correção de SQL**: Se o BQ reclama da query, o agente pega o erro e tenta de novo.
- **State Management**: Todo o contexto (chat history + tool results) fica no estado do grafo.

## 2. Ferramentas (Tools)

Tools que o agente usa pra interagir com o GCP:
1.  **get_data_dictionary**: Bate no `INFORMATION_SCHEMA` do BQ pra mapear as tabelas.
2.  **media_performance_queries**: Templates prontos pra ROI, conversão, etc.
3.  **generic_bq_explorer**: Query ad-hoc com filtros de segurança.

## 3. Segurança e Custos

Trava de segurança pra não queimar crédito:
- **max_token_cost**: Definido no `.env`. Se bater o teto, o fluxo mata o processo.
- **Token Auditor**: Callback que monitora `total_tokens` e `total_cost` via hooks da OpenAI.
- **Retry (Tenacity)**: Backoff exponencial pra não travar em erro 429 ou instabilidade de rede.

## 4. Estrutura (Clean Archish)

Organização do repo:
```text
/app
├── api/             # FastAPI routes
├── core/            # Configs (Pydantic) e Errors
├── services/        # Infra clients (BigQuery)
├── agent_logic/     # Grafos, Tools e Prompts
└── tests/           # Pytest + Mocks
```

## 5. Fluxo da Request

1.  **Entrypoint**: POST `/ask` com a dúvida do usuário.
2.  **Init**: LangGraph starta o estado inicial.
3.  **Loop ReAct**:
    - Decisão de tool -> Execução no BQ -> Observação do resultado.
4.  **Audit**: Checa custo final e fecha o log.
5.  **Output**: Resposta final em texto + metadados (custo, model, tools).

---
*Escalabilidade e controle de custo em primeiro lugar.*
