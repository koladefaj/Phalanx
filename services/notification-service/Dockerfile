FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library first
COPY shared/ /shared/

# Copy dependency manifest
COPY services/notification-service/pyproject.toml ./

# Install pip dependencies directly (no poetry needed — setuptools build system)
RUN pip install --no-cache-dir \
    "grpcio>=1.78.0,<2.0.0" \
    "sqlalchemy>=2.0.48,<3.0.0" \
    "alembic>=1.18.4,<2.0.0" \
    "asyncpg>=0.31.0,<0.32.0" \
    "aioboto3>=15.5.0,<16.0.0" \
    "httpx>=0.28.0,<0.29.0" \
    "pydantic-settings>=2.9.1,<3.0.0" \
    "protobuf>=7.34.0,<8.0.0"

# Install shared aegis_shared package
RUN pip install /shared

# Copy application code and alembic migrations
COPY services/notification-service/app/ ./app/
COPY services/notification-service/alembic/ ./alembic/
COPY services/notification-service/alembic.ini ./

EXPOSE 50055

CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
