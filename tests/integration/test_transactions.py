"""Integration tests for the transaction pipeline.

These tests run against the live Docker Compose stack and exercise real
service boundaries — no mocks. This is intentional: the most valuable
bugs in this system live at service boundaries (gRPC proto field mapping,
Redis key naming, SQS payload shape) that mocked unit tests would pass
even when broken.

Run with:
    pytest tests/integration/ -v

Prerequisites:
    docker compose up -d
    python generate_seed_data.py && cat seed_data.sql | docker exec -i aegis-risk-postgres-1 psql -U aegis
"""

import threading
import time

import pytest

from tests.integration.conftest import high_risk_payload, low_risk_payload


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post_txn(client, payload: dict):
    """Submit a transaction and return the parsed response dict."""
    resp = client.post("/transactions", json=payload)
    return resp


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class TestResponseSchema:
    """The response must contain every field the API contract promises."""

    def test_response_has_required_fields(self, client, run_id):
        key = f"schema-{run_id}"
        resp = post_txn(client, low_risk_payload(key))
        assert resp.status_code == 202, resp.text
        data = resp.json()

        required_fields = {
            "transaction_id",
            "status",
            "risk_score",
            "ml_score",
            "rule_score",
            "risk_factors",
            "decision",
            "already_existed",
        }
        missing = required_fields - data.keys()
        assert not missing, f"Response missing fields: {missing}\nFull response: {data}"

    def test_ml_score_propagated(self, client, run_id):
        """ml_score must be non-zero for an established account (good_user_01 is seeded).

        This test specifically guards against the mapper gap where from_evaluate_proto()
        copies rule_score but omits ml_score — a bug that passed all unit tests because
        the mapper was never called against a real proto response.
        """
        key = f"ml-{run_id}"
        resp = post_txn(client, low_risk_payload(key))
        assert resp.status_code == 202, resp.text
        data = resp.json()

        assert data["ml_score"] > 0.0, (
            "ml_score is 0.0 — this indicates the ML service returned a fallback score "
            "or the proto mapper is missing the ml_score field. "
            f"Full response: {data}"
        )

    def test_risk_score_in_valid_range(self, client, run_id):
        key = f"range-{run_id}"
        resp = post_txn(client, low_risk_payload(key))
        assert resp.status_code == 202
        data = resp.json()
        assert 0.0 <= data["risk_score"] <= 1.0, f"risk_score out of range: {data['risk_score']}"
        assert 0.0 <= data["ml_score"] <= 1.0, f"ml_score out of range: {data['ml_score']}"
        assert 0.0 <= data["rule_score"] <= 1.0, f"rule_score out of range: {data['rule_score']}"

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Risk Decisions
# ---------------------------------------------------------------------------

class TestRiskDecisions:
    """The engine must produce the right decision for known scenarios."""

    def test_low_risk_sender_approved(self, client, run_id):
        """good_user_01 has 6 months of clean domestic history — must APPROVE."""
        key = f"approve-{run_id}"
        resp = post_txn(client, low_risk_payload(key))
        assert resp.status_code == 202, resp.text
        data = resp.json()

        assert data["status"] == "APPROVED", (
            f"Expected APPROVED for known sender on domestic low-value payment. "
            f"Got {data['status']}. risk_score={data.get('risk_score')}, "
            f"risk_factors={data.get('risk_factors')}"
        )
        assert data["risk_score"] < 0.5, (
            f"APPROVED transaction has suspiciously high risk_score: {data['risk_score']}"
        )

    def test_high_risk_blocked(self, client, run_id):
        """Fresh account + £14.5k + GB→RU high-risk corridor + unknown device must not APPROVE.

        This combination fires: AccountAgeRule (HIGH, score=1.0), GeoMismatch (HIGH, score=0.9),
        HighValue (MEDIUM, score=0.56), DeviceFingerprintRule (MEDIUM), NewReceiverRule (MEDIUM).
        Combined rule_score exceeds the BLOCK threshold.
        """
        key = f"block-{run_id}"
        resp = post_txn(client, high_risk_payload(run_id, key))
        assert resp.status_code == 202, resp.text
        data = resp.json()

        assert data["status"] in ("BLOCKED", "REVIEW"), (
            f"Expected BLOCKED or REVIEW for high-risk payload. "
            f"Got {data['status']}. risk_score={data.get('risk_score')}"
        )

    def test_risk_factors_present_for_flagged_transaction(self, client, run_id):
        """Flagged transactions must have at least one risk_factor explaining the decision."""
        key = f"factors-{run_id}"
        resp = post_txn(client, high_risk_payload(run_id, key))
        assert resp.status_code == 202, resp.text
        data = resp.json()

        if data["status"] in ("BLOCKED", "REVIEW"):
            assert len(data["risk_factors"]) > 0, (
                f"Transaction with status={data['status']} has no risk_factors. "
                "The engine must provide at least one factor for auditability."
            )


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:
    """Duplicate submissions must be handled safely and consistently."""

    def test_duplicate_key_returns_same_transaction(self, client, run_id):
        """Submitting the same payload twice must return the same transaction_id."""
        key = f"idem-{run_id}"
        payload = low_risk_payload(key)

        first_resp = post_txn(client, payload)
        second_resp = post_txn(client, payload)

        assert first_resp.status_code == 202, first_resp.text
        assert second_resp.status_code == 202, second_resp.text

        first = first_resp.json()
        second = second_resp.json()

        assert first["transaction_id"] == second["transaction_id"], (
            "Duplicate submission returned a different transaction_id — "
            "the idempotency layer is not working correctly."
        )
        assert first["already_existed"] is False, "First submission should have already_existed=false"
        assert second["already_existed"] is True, "Second submission should have already_existed=true"

    def test_duplicate_key_with_different_amount_rejected(self, client, run_id):
        """Same idempotency key with a different amount must be rejected as a conflict.

        This prevents a client from silently changing the transaction details
        on a retry — a subtle but serious financial integrity bug.
        """
        key = f"conflict-{run_id}"
        original_payload = low_risk_payload(key)
        conflicting_payload = {**original_payload, "amount": 99999.00}

        first_resp = post_txn(client, original_payload)
        assert first_resp.status_code == 202, first_resp.text

        conflict_resp = post_txn(client, conflicting_payload)
        assert conflict_resp.status_code in (400, 409, 422), (
            f"Expected 4xx for idempotency key conflict (same key, different amount). "
            f"Got {conflict_resp.status_code}: {conflict_resp.text}"
        )


# ---------------------------------------------------------------------------
# Velocity Rule
# ---------------------------------------------------------------------------

class TestVelocityRule:
    """The velocity rule must fire when a sender exceeds the transaction threshold."""

    def test_velocity_spike_triggers_review(self, client, run_id):
        """5 cross-border transactions from a fresh sender must trip the velocity rule.

        Scoring breakdown for the 5th transaction:
        - VelocityRule: score=1.0 (HIGH) — count=5, excess=2
        - GeoMismatch: score=0.7 (HIGH) — GB→RU, medium amount
        - AccountAgeRule: score=0.3 (MEDIUM) — fresh account, $500

        Two HIGH-severity rules with boost → combined rule_score ~69 → MEDIUM → REVIEW.
        Transactions 1–4 are APPROVE; the 5th trips the threshold.
        """
        sender_id = f"vel_tester_{run_id}"
        base_payload = {
            "amount": 500.00,
            "currency": "GBP",
            "sender_id": sender_id,
            "receiver_id": "crypto_exchange",
            "sender_country": "GB",
            "receiver_country": "RU",
            "device_fingerprint": "vel_test_device",
            "ip_address": "10.0.0.1",
            "channel": "web",
            "transaction_type": "TRANSFER",
        }

        statuses = []
        for i in range(5):
            resp = post_txn(client, {**base_payload, "idempotency_key": f"vel-{run_id}-{i}"})
            assert resp.status_code == 202, f"Request {i} failed: {resp.text}"
            statuses.append(resp.json()["status"])

        assert statuses[-1] in ("REVIEW", "BLOCKED"), (
            f"Expected the 5th transaction from a velocity-spiking sender to be REVIEW or BLOCKED. "
            f"Statuses: {statuses}. "
            "Check that the velocity counter Redis key 'velocity:1h:{sender_id}' is incrementing "
            "correctly and that VELOCITY_MAX_TRANSACTIONS=3 in risk-engine config."
        )


# ---------------------------------------------------------------------------
# SLA
# ---------------------------------------------------------------------------

class TestSLA:
    """Performance contracts — warm path must stay within measured SLA bounds."""

    def test_warm_request_under_500ms(self, client, run_id):
        """A warm request (not first after cold start) must complete within 500ms.

        Measured P95 on local Docker Compose is ~200ms. 500ms gives 2.5x headroom
        for slower dev machines and Docker overhead variability.
        """
        # Warm-up: ensure gRPC channels are established
        post_txn(client, low_risk_payload(f"warmup-{run_id}"))

        key = f"sla-{run_id}"
        start = time.perf_counter()
        resp = post_txn(client, low_risk_payload(key))
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert resp.status_code == 202, resp.text
        assert elapsed_ms < 500, (
            f"Request took {elapsed_ms:.0f}ms, exceeding the 500ms SLA. "
            "This may indicate a cold-start — try again after the stack is fully warmed. "
            "Expected warm P95: ~200ms."
        )

    def test_20_concurrent_requests_under_800ms_p95(self, client, run_id):
        """20 concurrent requests from the same sender must all complete within 800ms P95.

        This exercises the Redis profile cache: after the first request, all 19 others
        should serve the profile from the 30s TTL cache rather than hitting Postgres.
        Measured P95 on local Docker: ~280ms.
        """
        times: list[float] = []
        errors: list[str] = []

        def send(idx: int):
            key = f"concurrent-{run_id}-{idx}"
            start = time.perf_counter()
            try:
                resp = post_txn(client, low_risk_payload(key))
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
                if resp.status_code != 202:
                    errors.append(f"req {idx}: HTTP {resp.status_code} — {resp.text[:200]}")
            except Exception as e:
                errors.append(f"req {idx}: {type(e).__name__}: {e}")

        threads = [threading.Thread(target=send, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Some concurrent requests failed:\n" + "\n".join(errors)

        sorted_times = sorted(times)
        p95_idx = int(len(sorted_times) * 0.95)
        p95_ms = sorted_times[p95_idx]

        assert p95_ms < 800, (
            f"P95 latency {p95_ms:.0f}ms exceeds 800ms for 20 concurrent requests. "
            f"All response times (ms): {[round(t) for t in sorted_times]}"
        )
