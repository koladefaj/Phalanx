FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install poetry    
RUN pip install --no-cache-dir --timeout 120 --retries 3 poetry

# Copy service code and dependency files
COPY services/transaction-service/pyproject.toml services/transaction-service/poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy shared library and install as a package
COPY shared/ /shared/
RUN pip install /shared

# Copy application code
COPY services/transaction-service/app/ ./app/

# Copy alembic versions
COPY services/transaction-service/alembic/ ./alembic/
COPY services/transaction-service/alembic.ini ./

# Expose service port
EXPOSE 50051

# Run service
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]