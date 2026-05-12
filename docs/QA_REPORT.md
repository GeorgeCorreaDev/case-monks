# Relatório de QA

Data: 12/05
Status: **pass** 

## Resumo da Suite

Rodei 7 testes cobrindo integração com BQ, endpoints FastAPI e o grafo do LangGraph.

| Suite | Status | O que foi testado |
| :--- | :--- | :--- |
| `test_bq_service` | OK | Esquemas e erros do BQ. |
| `test_api_v1` | OK | Endpoints e Health Check. |
| `test_monks_agent` | OK | Ciclo ReAct, Tools e trava de custo. |

## Robustez

1.  **Retry**: Tenacity com backoff exponencial pra falha de rede.
2.  **Budget**: `max_token_cost` segurando o gasto.
3.  **Tool Check**: Validação se o LangChain subiu os componentes certo.

## Validação Real (E2E)

Validação o agente com queries reais via `bigquery-public-data`:
- **ROI/Receita**: Consistente com agregação SQL.
- **Insights**: Agente gerou recomendações acionáveis além dos dados brutos.
- **Performance**: Tempo de resposta médio < 10s (incluindo BQ query).

## Próximos Passos

-   **CI/CD**: Plugar no GitHub Actions pra rodar em cada PR.
-   **Drift**: Monitorar se o schema do BQ mudar.
-   **Load Test**: Ver como o FastAPI aguenta concorrência alta.

---
*Relatório gerado via suite de testes automatizada e validação manual.*
