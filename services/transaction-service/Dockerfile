FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --timeout 120 --retries 3 poetry

COPY services/transaction-service/pyproject.toml services/transaction-service/poetry.lock* ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

COPY shared/ /shared/
RUN pip install /shared

COPY services/transaction-service/app/ ./app/
COPY services/transaction-service/alembic/ ./alembic/
COPY services/transaction-service/alembic.ini ./

EXPOSE 50051

CMD ["python", "-m", "app.main"]