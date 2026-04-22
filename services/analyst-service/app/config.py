from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://aegis:aegis_secret@postgres:5432/aegis_risk"

    # LLM Provider settings (Loose Coupling)
    LLM_PROVIDER: str = "ollama"  # 'ollama', 'gemini', 'openai', 'anthropic'
    LLM_MODEL: str = "gemma3:12b"
    LLM_BASE_URL: str = "http://host.docker.internal:11434" # Used primarily for ollama
    
    # Optional API Keys for other providers
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # gRPC settings
    ANALYST_SERVICE_GRPC_PORT: int = 50056
    CORRELATION_ID_HEADER: str = "X-Correlation-ID"
    ML_SERVICE_HOST: str = "ml-service"
    ML_SERVICE_GRPC_PORT: int = 50053

    # AWS / SQS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_ENDPOINT_URL: str = "http://localstack:4566"

    # SQS queues
    SQS_AGENT_INVESTIGATIONS_QUEUE: str = "aegis-agent-investigations"
    SQS_AGENT_INVESTIGATIONS_DLQ: str = "aegis-agent-investigations-dlq"
    SQS_RETRAIN_QUEUE: str = "aegis-model-retrain-requests"

    # Worker settings
    WORKER_POLL_INTERVAL: int = 5
    WORKER_VISIBILITY_TIMEOUT: int = 180   # 3 min — gives LLM breathing room
    WORKER_MAX_MESSAGES: int = 5           # processed concurrently; 5 is safe for local LLMs
    WORKER_MAX_RETRIES: int = 3            # stop retrying after this many attempts (belt + DLQ suspenders)
    WORKER_ID: str = "agent-worker-1"      # override via env for multiple replicas: WORKER_ID=agent-worker-2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
