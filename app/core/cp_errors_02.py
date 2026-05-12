# erors do sistema,, cada camada lanca o seu
# facilita debug e vira http status no fastapi

class monks_base_error(Exception):
    # base de tudo

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details})"


class bq_execution_error(monks_base_error):
    # falha no bq (rede, sql, auth)
    pass


class bq_validation_error(monks_base_error):
    # params zoados antes de ir pro bq
    pass


class agent_logic_error(monks_base_error):
    # erro no grafo ou no loop do agente
    pass


class llm_provider_error(monks_base_error):
    # timeout ou quota no llm
    pass


class scope_error(monks_base_error):
    # pergunta que nao eh de midia/trafego
    pass

