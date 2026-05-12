# automação de ambiente para o Case tecnico 
.PHONY: install run test lint help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala dependências usando uv"
	@echo "  make run      - Executa a API localmente"
	@echo "  make test     - Executa os testes automatizados com pytest"
	@echo "  make lint     - Executa verificação de tipos e estilo (ruff)"

install:
	uv sync

run:
	uv run python app/run.py

test:
	uv run pytest app/tests -v --color=yes

lint:
	uv run ruff check .
	uv run mypy app
