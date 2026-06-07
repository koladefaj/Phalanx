"""Integration test fixtures and helpers.

These tests run against the live Docker Compose stack. Start it first:
    docker compose up -d
    python generate_seed_data.py && cat seed_data.sql | docker exec -i aegis-risk-postgres-1 psql -U aegis

Set AEGIS_BASE_URL to override the default (http://localhost:8000).
Set AEGIS_TENANT_ID to override the default test tenant.
"""

import os
import uuid

import pytest
import httpx

BASE_URL = os.getenv("AEGIS_BASE_URL", "http://localhost:8000")
TENANT_ID = os.getenv("AEGIS_TENANT_ID", "56f292e4-80f1-704a-38f4-42f883cf5d91")

_DEV_HEADERS = {
    "Content-Type": "application/json",
    "X-Dev-Tenant-Id": TENANT_ID,
}


@pytest.fixture(scope="session")
def client():
    """Sync HTTP client pointing at the running Docker stack.

    Session-scoped so gRPC channels warm up once and all tests share
    the same warm connection pool.
    """
    with httpx.Client(base_url=BASE_URL, headers=_DEV_HEADERS, timeout=30.0) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def require_stack(client):
    """Fail fast with a clear message if the Docker stack isn't running."""
    try:
        resp = client.get("/health")
        assert resp.status_code == 200, f"Health check returned {resp.status_code}"
    except httpx.ConnectError:
        pytest.exit(
            f"\n\nStack is not reachable at {BASE_URL}.\n"
            "Run `docker compose up -d` and wait ~30s for all services to start.\n"
            "Then re-run: pytest tests/integration/ -v\n",
            returncode=1,
        )


@pytest.fixture
def run_id() -> str:
    """Short random ID to namespace all test resources within a single run.

    Using a per-test unique run_id ensures:
    - Idempotency keys never clash between tests
    - Velocity/profile counters start fresh for each test's sender
    """
    return uuid.uuid4().hex[:10]


# ---------------------------------------------------------------------------
# Payload builders — module-level functions, not fixtures, so they can be
# called with arbitrary parameters inside test methods.
# ---------------------------------------------------------------------------

def low_risk_payload(key: str) -> dict:
    """Known sender + known device + domestic GBP payment.

    good_user_01 is pre-seeded with 6 months of clean history.
    Expected decision: APPROVE.
    """
    return {
        "amount": 250.00,
        "currency": "GBP",
        "sender_id": "good_user_01",
        "receiver_id": "merchant_trusted",
        "sender_country": "GB",
        "receiver_country": "GB",
        "device_fingerprint": "device_good_1",
        "ip_address": "192.168.1.5",
        "idempotency_key": key,
        "channel": "web",
        "transaction_type": "PAYMENT",
    }


def high_risk_payload(run_id: str, key: str) -> dict:
    """Fresh account + high value + GB→RU high-risk corridor + unknown device.

    Uses a unique sender_id per run so there's no shared profile history
    and no velocity bleed-over from previous test runs.
    Expected decision: BLOCK.
    """
    return {
        "amount": 14500.00,
        "currency": "GBP",
        "sender_id": f"fresh_sender_{run_id}",
        "receiver_id": "shady_crypto_wallet",
        "sender_country": "GB",
        "receiver_country": "RU",
        "device_fingerprint": f"unknown_device_{run_id}",
        "ip_address": "103.45.2.19",
        "idempotency_key": key,
        "channel": "mobile_app",
        "transaction_type": "TRANSFER",
    }
