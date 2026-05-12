
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev


FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r monks && useradd -r -g monks monks

COPY --from=builder /app/.venv /app/.venv
COPY . .

RUN chown -R monks:monks /app

USER monks

EXPOSE 8000
EXPOSE 8501

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "run.py"]
