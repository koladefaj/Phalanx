from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ML service settings."""

    ENVIRONMENT: str
    LOG_LEVEL: str = "INFO"
    CORRELATION_ID_HEADER: str

    # gRPC
    GRPC_TIMEOUT: int
    GRPC_USE_TLS: bool
    ML_SERVICE_GRPC_PORT: int = 50053

    # model
    MODEL_PATH: str = "models/risk_model.onnx"
    FEATURE_NAMES_PATH: str = "models/features.json"
    THRESHOLD_PATH: str = "models/metadata.json"
    PAYSIM_DATA_PATH: str = "app/data/paysim.csv"
    MODEL_VERSION: str = "1.0.0"

    # AWS / S3 (For Hot-Swapping)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_ENDPOINT_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()