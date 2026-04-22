FROM python:3.12-slim

WORKDIR /app

# Install gcc for compiling dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only pyproject.toml + poetry.lock first for caching
COPY services/analyst-service/pyproject.toml services/analyst-service/poetry.lock* ./

# Disable virtualenvs, install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root
RUN pip install protobuf aioboto3 structlog

# Copy shared libraries, proto files, and service code
COPY shared/ /shared/
RUN pip install /shared
COPY proto/ /proto/
COPY services/analyst-service/app/ ./app/

# Expose service port
EXPOSE 50056

# Run service
CMD ["python", "-m", "app.main"]