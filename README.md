# Agent Media Analyst 

Agente autônomo de BI para análise de mídia e performance. O sistema orquestra consultas no Google BigQuery através de linguagem natural, utilizando LangGraph para gerenciamento de estado e memória conversacional.

## Core Features
- **Conversational Memory**: Persistência de estado via MemorySaver (Short-term context).
- **Multi-LLM Engine**: Abstração via Factory Pattern suportando OpenAI, Anthropic e Google Gemini.
- **BQ Query Caching**: Camada de cache in-memory para redução de latência e custos de processamento (GCP Slots).
- **Security**: Autenticação via X-API-KEY e validação de envs através de Pydantic Settings.
- **Observability**: Tracking detalhado de uso de tokens e custo por request.

## Stack Técnica
- Python 3.12+ (uv manager)
- FastAPI (Backend API)
- Streamlit (Frontend Dashboard)
- LangGraph / LangChain (LLM Orchestration)
- Google BigQuery (Data Warehouse)
- Docker / Docker-Compose (Containerization)

## Dashboard Frontend (Streamlit)
O projeto conta com uma interface gráfica (UI) simples e elegante construída com **Streamlit**, desenhada para se comunicar diretamente com o meu backend FastAPI de forma amigável para o analista e gestor.

**O que o Dashboard oferece:**
- **Interface de Chat**: Comunicação fluida com o Agente do Case Tecnico em linguagem natural.
- **Observabilidade de Custos**: Exibe a contagem exata de tokens utilizados e o custo em dólares (USD) a cada interação.
- **Histórico Persistente na Sessão**: A thread (contexto) da conversa se mantém enquanto a página não for recarregada.
- **Style**: Possui estilo dark mode nativo via CSS injetado e gerenciamento robusto de requisições.

A comunicação entre a UI e a API principal acontece na rota `/api/v1/ask`.

## Execução

### 1. Setup Ambiental
Crie o arquivo `.env` no diretório `app/` seguindo o `app/.env.ex`. Certifique-se de incluir a `API_KEY_INTERNAL` e os tokens dos LLMs desejados.

### 2. Docker Orchestration (API + Frontend)
A forma recomendada de execução é via Docker Compose, que orquestra o backend e a interface visual:
```bash
docker-compose up --build
```
- API: `http://localhost:8000`
- Streamlit UI: `http://localhost:8501`

### 3. Execução Local (Dev)
Caso prefira rodar fora de containers:
```bash
make install
make run
```

## Qualidade e Testes
Suite de testes automatizada cobrindo mocks de infraestrutura (BQ e LLM):
```bash
make test
```

## Arquitetura e Decisões
O histórico de decisões técnicas e a estrutura detalhada do grafo de agentes podem ser encontrados em:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/ADR/](docs/ADR/)
- [docs/img-QA/](docs/img-QA/) imagens da POC | QA test validation

---
* Case Tecnico- Autor George A. Corrêa  - 12/05/2026 *
