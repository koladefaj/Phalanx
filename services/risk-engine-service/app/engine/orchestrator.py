"""Risk scoring orchestrator — combines rule-based and ML results.

LLM explanation is NOT called inline — it's too slow for the <300ms SLA.
The orchestrator returns a RiskAssessment immediately after ML scoring.
LLM explanation is triggered async via SQS and delivered via webhook.
"""

import asyncio
import json
import time
from decimal import Decimal
from typing import Optional, Any

from app.db.session import get_session

from app.config import settings
from app.engine.scorer import RiskScorer
from app.engine.rules import get_all_rules
from app.grpc.clients.ml_client import MLGRPCClient
from app.grpc.clients.analyst_client import AnalystClient
from app.repositories.account_profile_repo import AccountProfileRepository
from app.repositories.risk_repo import RiskResultRepository
from aegis_shared.schemas.risk import RiskAssessment
from aegis_shared.utils.logging import get_logger

logger = get_logger("orchestrator")


class RiskOrchestrator:
    """Orchestrates the synchronous risk evaluation pipeline.

    Flow:
        1. Load account profile from DB (or create if new account)
        2. Enrich transaction dict with behavioural features
        3. Run all rule-based checks
        4. Call ML service for anomaly score (with fallback)
        5. Calculate combined score → RiskLevel → RiskDecision
        6. Return RiskAssessment immediately (<300ms)

    LLM explanation is NOT part of this flow — it runs async via SQS
    consumer and is delivered to the bank via webhook.
    """

    def __init__(self, scorer: RiskScorer, ml_client: MLGRPCClient, analyst_client: AnalystClient | None = None):
        self.rules = get_all_rules()
        self.scorer = scorer
        self.ml_client = ml_client
        self.analyst_client = analyst_client

    async def evaluate(self, transaction_data: dict) -> RiskAssessment:
        """Run the synchronous risk evaluation pipeline.

        Args:
            transaction_data: Transaction fields from EvaluateRiskRequest.

        Returns:
            RiskAssessment — returned immediately to transaction-service.
        """
        start_time = time.perf_counter()
        transaction_id = transaction_data.get("transaction_id", "unknown")
        sender_id = transaction_data.get("sender_id", "")
        amount = Decimal(str(transaction_data.get("amount", 0)))

        logger.info("risk_evaluation_started", transaction_id=transaction_id)

        # Step 1: Load account profile (Redis cache → DB fallback)
        profile = await self._load_profile_cached(sender_id)

        # Step 2: Enrich transaction with behavioural features
        device_fp = transaction_data.get("device_fingerprint") or ""
        receiver_id = transaction_data.get("receiver_id") or ""

        is_new_device = profile.is_new_device(device_fp)
        is_new_receiver = profile.is_new_receiver(receiver_id)

        try:
            from aegis_shared.utils.redis import get_redis
            redis_client = get_redis()

            device_key = f"burst:device:{sender_id}"
            receiver_key = f"burst:receiver:{sender_id}"
            velocity_key = f"velocity:1h:{sender_id}"
            failed_key = f"failed:1h:{sender_id}"

            async def _sadd_device():
                if is_new_device and device_fp:
                    return await redis_client.sadd(device_key, device_fp)
                return 1

            async def _sadd_receiver():
                if is_new_receiver and receiver_id:
                    return await redis_client.sadd(receiver_key, receiver_id)
                return 1

            # All four Redis reads/writes are independent — run concurrently
            device_result, receiver_result, redis_txn_count, redis_failed = await asyncio.gather(
                _sadd_device(),
                _sadd_receiver(),
                redis_client.incr(velocity_key),
                redis_client.get(failed_key),
            )

            if device_result == 0:
                is_new_device = False
            if receiver_result == 0:
                is_new_receiver = False

            redis_failed_count = int(redis_failed) if redis_failed else profile.blocked_txn_count

            # TTL refreshes don't affect correctness — fire without blocking the hot path
            asyncio.create_task(redis_client.expire(device_key, 300))
            asyncio.create_task(redis_client.expire(receiver_key, 300))
            asyncio.create_task(redis_client.expire(velocity_key, 3600))

        except Exception as e:
            logger.warning("redis_burst_cache_error", error=str(e), transaction_id=transaction_id)
            redis_txn_count = profile.txn_count_1h
            redis_failed_count = profile.blocked_txn_count

        # Use Redis count (real-time) over DB profile count (async lag)
        transaction_data["metadata"] = {
            "account_age_days": profile.account_age_days,
            "recent_transaction_count": redis_txn_count,      # ✅ Redis not DB
            "recent_failed_count": redis_failed_count,         # ✅ Redis not DB
            "known_devices": profile.known_device_fingerprints or [],
            "is_new_device": is_new_device,
            "is_new_receiver": is_new_receiver,
            "known_receivers": profile.known_receiver_ids or [],
            "fraud_txn_count": profile.fraud_txn_count,
            "is_high_risk_account": profile.is_high_risk,
        }

        # Step 3: Run all rules
        rule_results = []
        for rule in self.rules:
            try:
                result = rule.evaluate(transaction_data)
                result["severity"] = self._score_to_severity(result["score"])
                rule_results.append(result)
            except Exception as e:
                logger.error(
                    "rule_evaluation_failed",
                    rule=rule.name,
                    error=str(e),
                    transaction_id=transaction_id,
                )
                rule_results.append({
                    "rule": rule.name,
                    "triggered": False,
                    "score": 0.0,
                    "severity": "LOW", 
                    "reason": f"Rule evaluation failed: {str(e)}",
                })

        rule_score = self.scorer.calculate_rule_score(rule_results)

        # Step 4: ML anomaly score (with fallback)
        ml_result = await self._get_ml_score(transaction_data, profile)

        # THE FIX: If it's a brand new account and a small amount, 
        # the ML model is statistically unreliable.
        if profile.account_age_days < 0.1 and amount < 250.0:
            logger.info(
                "suppressing_ml_for_new_user_onboarding", 
                transaction_id=transaction_id, 
                original_anomaly_score=ml_result["anomaly_score"]
            )
            ml_result["anomaly_score"] = float(Decimal(str(ml_result["anomaly_score"])) * Decimal("0.1"))

        # Step 5: Calculate final score → level → decision
        final_score = self.scorer.calculate_final_score(
            rule_score=rule_score,
            ml_score=ml_result["anomaly_score"],
            rule_weight=settings.RULE_SCORE_WEIGHT,
            ml_weight=settings.ML_SCORE_WEIGHT,
        )

        risk_level = self.scorer.categorize_risk(final_score)
        decision = self.scorer.make_decision(risk_level)

        # debug logs AFTER all values are computed
        logger.info(
            "rule_scores_debug",
            transaction_id=transaction_id,
            rules=[{
                "rule": r["rule"],
                "triggered": r.get("triggered"),
                "score": r.get("score"),
            } for r in rule_results],
            total_rules=len(rule_results),
            rule_score=rule_score,
            final_score=final_score,
        )

        # Step 6: Build risk factors list for explanation — triggered rules + ML anomaly
        risk_factors = [
            {
                "factor": r["rule"],
                "severity": self._score_to_severity(r["score"]),
                "detail": r["reason"],
            }
            for r in rule_results
            if r.get("triggered", False)
        ]

        # Explicitly add ML Anomaly if it's significant (> 0.5)
        if ml_result["anomaly_score"] > 0.5:
            risk_factors.append({
                "factor": "ML_ANOMALY_DETECTION",
                "severity": "HIGH" if ml_result["anomaly_score"] > 0.8 else "MEDIUM",
                "detail": f"Unusual behavioral pattern detected by XGBoost model (Score: {ml_result['anomaly_score']:.2f})"
            })

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "risk_evaluation_completed",
            transaction_id=transaction_id,
            risk_score=round(final_score, 2),
            risk_level=risk_level.value,
            decision=decision.value,
            processing_time_ms=round(processing_time_ms, 2),
            rules_triggered=len(risk_factors),
            ml_fallback=ml_result.get("fallback_used", False),
        )

        logger.info(
            "orchestrator_returning",
            transaction_id=transaction_id,
            decision=decision.value,
            risk_level=risk_level.value,
            final_score=final_score,
            rule_score=rule_score,
        )

        return RiskAssessment(
            transaction_id=transaction_id,
            decision=decision,
            risk_score=round(final_score / 100, 4),
            risk_level=risk_level,
            confidence=self._score_to_confidence(final_score),
            risk_factors=risk_factors,
            rule_score=round(rule_score / 100, 4),
            ml_score=round(ml_result.get("anomaly_score", 0.0), 4),
            processing_time_ms=round(processing_time_ms, 2),
            model_version=ml_result.get("model_version", "1.0.0"),
        )

    async def _load_profile_cached(self, sender_id: str):
        """Load account profile from Redis cache, falling back to Postgres on miss.

        Cache TTL is 30s — short enough that stale is_high_risk flags are tolerable,
        long enough to absorb concurrent requests from the same sender.
        """
        from aegis_shared.utils.redis import get_redis
        from app.models.account_profile import AccountProfile

        try:
            redis_client = get_redis()
            cached = await redis_client.get(f"profile:{sender_id}")
            if cached:
                return AccountProfile.from_cache_dict(json.loads(cached))
        except Exception:
            pass

        async with get_session() as session:
            profile_repo = AccountProfileRepository(session)
            profile = await profile_repo.get_or_create(sender_id)

        try:
            redis_client = get_redis()
            asyncio.create_task(
                redis_client.setex(f"profile:{sender_id}", 30, json.dumps(profile.to_cache_dict()))
            )
        except Exception:
            pass

        return profile

    async def _get_ml_score(self, transaction_data: dict, profile) -> dict:
        """Get ML anomaly score with graceful fallback.

        Passes both raw transaction fields and derived profile features
        to ml-service so it has the full feature vector.
        """
        try:
            feature_vector = profile.to_feature_dict(
                current_amount=Decimal(str(transaction_data.get("amount", 0))),
                receiver_id=transaction_data.get("receiver_id", ""),
                device_fingerprint=transaction_data.get("device_fingerprint", ""),
            )
            return await self.ml_client.score_transaction(
                transaction_data=transaction_data,
                features=feature_vector,
            )
        except Exception as e:
            logger.warning(
                "ml_service_fallback",
                error=str(e),
                transaction_id=transaction_data.get("transaction_id"),
            )
            return {
                "anomaly_score": 0.0,  
                "model_version": "fallback",
                "fallback_used": True,
            }
        
    async def _get_analyst_investigation(self, transaction_id, sender_id, correlation_id="") -> dict:
        """Call AI Analyst service for investigation, with fallback."""
        if not self.analyst_client:
            return {
                "summary": f"Analyst analysis unavailable for transaction {transaction_id}.",
                "verdict": "SUSPICIOUS",
                "recommendation": "REVIEW",
                "confidence": "LOW",
                "agent_name": "fallback",
                "fallback_used": True
            }
            
        return await self.analyst_client.investigate_transaction(
            transaction_id=transaction_id,
            sender_id=sender_id,
            correlation_id=correlation_id,
        )

    async def get_result(self, transaction_id: str) -> Optional[RiskAssessment]:
        """Fetch a stored risk result from the database."""
        async with get_session() as session:
            repo = RiskResultRepository(session)
            return await repo.get_by_transaction_id(transaction_id)

    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Convert a rule score (0–1) to a severity label."""
        if score >= 0.8:
            return "HIGH"
        if score >= 0.5:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _score_to_confidence(final_score: float) -> str:
        """Confidence is high when score is clearly in one zone."""
        # High confidence when far from thresholds
        if final_score <= 25 or final_score >= 85:
            return "HIGH"
        # Low confidence near decision boundaries
        if 35 <= final_score <= 55:
            return "LOW"
        return "MEDIUM"