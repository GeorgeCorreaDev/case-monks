# ADR 0001: LangGraph pra Orquestração

**Data**: 12/05
**Status**: pass

## Contexto
Precisamos de um agente autônomo pra bater no BQ (BigQuery). Testei o AgentExecutor legado do LangChain.

## Decisão
Bora de **LangGraph**.

## Justificativa
1.  **Controle do Grafo**: Diferente do AgentExecutor, no LangGraph a gente desenha o StateGraph e controla o loop ReAct na mão. Evita loop infinito e facilita o debug.
2.  **Persistência**: Fica fácil salvar o estado e implementar memória com checkpointers.
3.  **Padrão de mercado**: É o que tem de mais moderno pra multi-tool agents hoje.
4.  **Extensibilidade**: Dá pra plugar validação custom ou human-in-the-loop sem gambiarra.
