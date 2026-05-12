import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


# schema de config valida as var de amb
# nota! usa pydtic pra evita err de tipagem no proj
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # llm .. provider via env (openai default)
    llm_provider: str = Field(default="openai", description="openai | anthropic | gemini")
    llm_model: str = Field(default="gpt-4o-mini")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    google_api_key: str = Field(default="")

    # segurança,, em prod usar gcp secret manager ou sops
    # para este mvp uso pydantic settings pra validar 
    api_key_internal: str = Field(default="monks-secret-key-2026", description="chave para auth basica da api")
    api_url: str = Field(default="http://localhost:8000/api/v1", description="url da api")

    # gcp projeto bq
    gcp_project_id: str = Field(default="")
    google_application_credentials: str = Field(default="")

    # app
    debug: bool = Field(default=False)
    max_token_cost: float = Field(default=0.10, description="limite maximo de custo por pergunta em usd")

    # cache
    enable_cache: bool = Field(default=True)


# singleton global > importa sem re instanciar
config = Settings()

if config.google_application_credentials:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_application_credentials
