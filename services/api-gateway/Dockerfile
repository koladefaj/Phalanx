FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY services/api-gateway/pyproject.toml services/api-gateway/poetry.lock* ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root


COPY shared/ /shared/
RUN pip install /shared

COPY proto/ /proto/
COPY services/api-gateway/app/ /app/app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]