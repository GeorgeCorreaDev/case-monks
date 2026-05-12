# Setup do Ambiente

Passo a passo pra subir o projeto e configurar as keys.

## 1. Pré-requisitos
- **Python 3.12+**
- **uv**: `pip install uv` (gerenciador de pacotes)
- **GCloud SDK**: Autenticado e com acesso ao BQ.
- **OpenAI API Key**: Pro cérebro do agente.

## 2. Instalação

```bash
# clone e entra na pasta
git clone <url-do-repo>
cd case_monks

# uv resolve o venv
make install
```

## 3. Env Vars (.env)

Cria o `.env` na pasta `/app`:

```env
# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# GCP
GCP_PROJECT_ID=teu-projeto-id
GOOGLE_APPLICATION_CREDENTIALS=./pasta/key.json

# Budget & Debug
MAX_TOKEN_COST=0.10
DEBUG=True
```

## 4. Auth no GCP

O agente usa o dataset público `thelook_ecommerce`. Precisa de `BigQuery Data Viewer` e `Job User`.

Autentica via ADC:
```bash
gcloud auth application-default login
```

## 5. Run & Test

### Subir a API
```bash
make run
```
Docs em `http://localhost:8000/docs`.

### Rodar Testes
```bash
make test
```
*Mocks ativos pra não gastar crédito no BQ/OpenAI.*

## Troubleshooting

- **Module not found**: Vê se o venv tá ativo ou usa `uv run`.
- **Quota Exceeded**: Aumenta o `MAX_TOKEN_COST` no env.
- **GCP Project**: Checa se o ID no env tá certo e tem billing ativo.

