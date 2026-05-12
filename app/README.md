# agent media analyst

mvp de um agente ia autonomo que atua como **analista junior de midia**, conectado ao bigquery publico `thelook_ecommerce`. recebe perguntas em linguagem natural sobre trafego/canais e retorna insights acionaveis — nao apenas tabelas brutas.

---

## stack

| camada | tech | pq |
|---|---|---|
| orquestração | langgraph (react agent) | controle explicito de estados, loop tool-call nativo |
| llm | openai (gpt-4o-mini default) | custo/beneficio pro mvp, troca via .env |
| data warehouse | google bigquery | dataset publico, zero infra propria |
| api | fastapi + uvicorn | async nativo, docs automaticos, validacao pydantic |
| config | pydantic-settings | tipagem forte, carrega .env automatico |
| deps | uv | rapido, lockfile deterministico |

---

## arquitetura

```
app/
├── core/                    # config e erros centralizados
│   ├── cp_config_01.py      # pydantic-settings, singleton global
│   └── cp_errors_02.py      # hierarquia de erros tipados
├── services/                # camada de dados
│   └── bq_service.py        # client bq lazy, queries parametrizadas
├── agent_logic/             # cerebro do agente
│   ├── tools.py             # 4 tools langchain com schemas pydantic v2
│   └── monks_agent.py       # grafo langgraph, system prompt, factory llm
├── api/                     # camada http
│   └── api_routes.py        # POST /ask + GET /health
├── run.py                   # entrypoint uvicorn
├── pyproject.toml           # deps e build config
└── .env.ex                  # exemplo de variaveis de ambiente
```

fluxo de uma request:

```
usuario → POST /api/v1/ask
  → ask_agent() cria grafo react
    → llm decide qual tool chamar
      → tool executa query parametrizada no bq
    → llm analisa resultado
    → llm gera insight em pt-br
  → resposta json pro cliente
```

---

## setup

### pre-requisitos

- python 3.12+
- [uv](https://docs.astral.sh/uv/) instalado
- conta gcp com acesso ao bigquery (dataset publico)
- chave api do llm provider (openai por default)

### instalacao

```bash
cd app
uv sync
```

### configuracao

```bash
cp .env.ex .env
# edite o .env com suas credenciais
```

variaveis obrigatorias:

| variavel | descricao | exemplo |
|---|---|---|
| `openai_api_key` | chave da api openai | `sk-proj-...` |
| `gcp_project_id` | projeto gcp pra billing do bq | `meu-projeto-gcp` |

autenticacao gcp — escolha uma:

```bash
# opcao 1: adc (recomendado pra dev local)
gcloud auth application-default login

# opcao 2: service account
# defina GOOGLE_APPLICATION_CREDENTIALS=/caminho/key.json no .env
```

### execucao

```bash
uv run python run.py
# servidor em http://localhost:8000
```

docs interativos: `http://localhost:8000/docs`

---

## api

### `GET /api/v1/health`

liveness check.

```json
{"status": "healthy", "version": "0.1.0"}
```

### `POST /api/v1/ask`

endpoint principal — recebe pergunta, retorna insight do agente.

**request:**

```json
{
  "question": "qual canal trouxe mais receita em 2024?"
}
```

**response:**

```json
{
  "answer": "resumo executivo com dados reais do bigquery...",
  "status": "ok"
}
```

**erros:**

| status | quando |
|---|---|
| 422 | pergunta fora do escopo de midia |
| 500 | falha no bq, llm ou erro nao tratado |

---

## tools disponiveis pro agente

o agente decide automaticamente qual ferramenta usar com base na pergunta:

| tool | o que faz | params |
|---|---|---|
| `get_revenue_by_channel` | receita, pedidos e usuarios por canal | start_date, end_date |
| `get_conversion_rate` | taxa de conversao por canal (compradores/total) | start_date, end_date |
| `get_ticket_medio` | ticket medio por canal (receita/pedidos) | start_date, end_date |
| `get_top_products` | top 10 produtos de um canal especifico | channel, start_date, end_date |

todas as queries usam **parametros bind** (`@param`) — zero risco de sql injection.

---

## dataset

usa o dataset publico `bigquery-public-data.thelook_ecommerce` que simula uma loja de roupas online.

tabelas utilizadas:

| tabela | uso |
|---|---|
| `users` | `traffic_source` como proxy pra canais de midia |
| `order_items` | pedidos, receita, status |
| `products` | nome e categoria dos produtos |

canais disponiveis no dataset: `Search`, `Organic`, `Facebook`, `Display`, `Email`

---

## decisoes tecnicas

- **queries parametrizadas**: todo input do usuario passa por `ScalarQueryParameter` do bq. nenhuma string eh interpolada direto no sql
- **lazy singleton**: o client do bq so conecta na primeira chamada real, nao no startup. facilita testes e reduz cold start
- **stateless por request**: cada chamada ao `/ask` cria um grafo novo. sem estado compartilhado entre requests
- **hierarquia de erros**: cada camada tem seu tipo de erro (`bq_execution_error`, `agent_logic_error`, etc). a api traduz pra http status adequado
- **temperature 0.1**: minimiza alucinacao do llm — queremos dados precisos, nao criatividade

---

## exemplos de perguntas

```
"qual canal trouxe mais receita nos ultimos 6 meses?"
"compare a taxa de conversao entre Search e Facebook em 2024"
"qual o ticket medio do canal Organic no Q1 de 2024?"
"quais os produtos mais vendidos via Email em janeiro de 2024?"
"como esta a performance do Display comparado ao Search?"
```


