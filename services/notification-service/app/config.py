from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORRELATION_ID_HEADER: str = "x-correlation-id"

    # gRPC
    NOTIFICATION_GRPC_PORT: int = 50055
    GRPC_TIMEOUT: int = 15

    # Database
    POSTGRES_USER: str = "aegis"
    POSTGRES_PASSWORD: str = "aegis_secret"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    NOTIFICATION_DB_NAME: str = "aegis_notifications"

    # AWS / SQS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_ENDPOINT_URL: str = "http://localstack:4566"
    SQS_RISK_COMPLETED_QUEUE: str = "aegis-risk-completed"

    # Webhook delivery
    WEBHOOK_SECRET: str = "webhook-signing-secret"
    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_TIMEOUT_SECONDS: int = 10

    # Worker
    WORKER_POLL_INTERVAL: int = 5
    WORKER_VISIBILITY_TIMEOUT: int = 30
    WORKER_MAX_MESSAGES: int = 10
    WORKER_ID: str = "notification-worker-1"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.NOTIFICATION_DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )


settings = Settings()
