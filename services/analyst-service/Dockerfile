FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY shared/ /shared/
RUN pip install --no-cache-dir /shared

COPY services/analyst-service/pyproject.toml ./

RUN pip install --no-cache-dir \
    "grpcio>=1.78.0" \
    "llama-index-core>=0.14.21,<0.15.0" \
    "llama-index-llms-ollama>=0.10.1" \
    "llama-index-llms-anthropic>=0.6.0" \
    "llama-index-llms-openai>=0.5.0" \
    "llama-index-llms-gemini>=0.5.0" \
    "instructor>=1.7.0" \
    "anthropic>=0.40.0" \
    "openai>=1.58.0" \
    "google-generativeai>=0.8.0" \
    "sqlalchemy>=2.0.49" \
    "asyncpg>=0.31.0" \
    "pydantic>=2.13.3" \
    "pydantic-settings>=2.14.0" \
    "httpx>=0.28.1" \
    "aioboto3>=13.4.0" \
    "structlog>=25.5.0" \
    "protobuf>=5.0.0" \
    "alembic>=1.15.0"

COPY proto/ /proto/
COPY services/analyst-service/app/ ./app/

EXPOSE 50056

CMD ["python", "-m", "app.main"]
