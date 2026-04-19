FROM python:3.12-slim

# Set environment variables for better Docker performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install gcc for compiling dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir --timeout 120 --retries 3 poetry

# Copy service code and dependency files
COPY services/ml-service/pyproject.toml services/ml-service/poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy shared library and install as a package
COPY shared/ /shared/
RUN pip install /shared

# Copy application code
COPY services/ml-service/app/ ./app/

# Train model at build time (skip if fails)
# Provide dummy config values so Pydantic validation passes during Docker build
ENV ENVIRONMENT=build \
    CORRELATION_ID_HEADER=x-correlation-id \
    GRPC_TIMEOUT=5 \
    GRPC_USE_TLS=false

RUN PYTHONPATH=. python -m app.scripts.trainer || echo "Model training skipped"

# Expose service port
EXPOSE 50053

# Run service
CMD ["python", "-m", "app.main"]