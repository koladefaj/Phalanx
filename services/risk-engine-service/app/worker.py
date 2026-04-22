"""SQS Worker — polls transaction queue and triggers async post-processing."""

import asyncio
import json
import time
import uuid
from decimal import Decimal

from aegis_shared.utils.redis import get_redis
from aegis_shared.utils.sqs import get_boto_session
from app.config import settings
from app.engine.orchestrator import RiskOrchestrator
from app.repositories.account_profile_repo import AccountProfileRepository
from app.repositories.risk_repo import RiskResultRepository
from app.db.session import get_session
from aegis_shared.schemas.risk import RiskAssessment, RiskFactor
from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.tracing import set_correlation_id, clear_correlation_id

logger = get_logger("risk_worker")


class RiskWorker:
    """SQS consumer for async post-processing after sync risk decision.

    This worker does NOT make the fraud decision — that happens synchronously
    in the gRPC servicer. This worker handles everything AFTER the decision:

        1. Update account_profiles with transaction data
        2. Persist full RiskResult to DB
        3. Publish investigation trigger to aegis-agent-investigations SQS
           (the analyst-service worker picks it up and writes back)
        4. Publish RiskCompleted event (for notification-service webhook)
        5. Delete message from queue
    """

    def __init__(self, orchestrator: RiskOrchestrator):
        self.session = get_boto_session()
        self._queue_url: str | None = None
        self._completed_queue_url: str | None = None
        self._analyst_queue_url: str | None = None
        self.orchestrator = orchestrator
        self.worker_id = str(settings.WORKER_ID)

    def _client(self):
        return self.session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        )

    async def _get_queue_url(self, queue_name: str, cached: str | None) -> str:
        if cached:
            return cached
        try:
            async with self._client() as client:
                response = await client.get_queue_url(QueueName=queue_name)
                return response["QueueUrl"]
        except Exception:
            return f"{settings.AWS_ENDPOINT_URL}/000000000000/{queue_name}"

    async def run(self, shutdown_event: asyncio.Event) -> None:
        self._queue_url = await self._get_queue_url(
            settings.SQS_TRANSACTION_QUEUE, self._queue_url
        )
        self._completed_queue_url = await self._get_queue_url(
            settings.SQS_RISK_COMPLETED_QUEUE, self._completed_queue_url
        )
        self._analyst_queue_url = await self._get_queue_url(
            settings.SQS_AGENT_INVESTIGATIONS_QUEUE, self._analyst_queue_url
        )

        logger.info("worker_started", worker_id=self.worker_id)

        while not shutdown_event.is_set():
            try:
                await self._poll_messages()
            except Exception as e:
                logger.error("worker_poll_error", error=str(e))
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

        logger.info("worker_stopped", worker_id=self.worker_id)

    async def _poll_messages(self) -> None:
        async with self._client() as client:
            response = await client.receive_message(
                QueueUrl=self._queue_url,
                MaxNumberOfMessages=settings.WORKER_MAX_MESSAGES,
                VisibilityTimeout=settings.WORKER_VISIBILITY_TIMEOUT,
                WaitTimeSeconds=5,
                MessageAttributeNames=["All"],
            )

        messages = response.get("Messages", [])
        if not messages:
            return

        logger.info("messages_received", count=len(messages))

        await asyncio.gather(
            *[self._process_message(msg) for msg in messages],
            return_exceptions=True,
        )

    async def _process_message(self, message: dict) -> None:
        receipt_handle = message["ReceiptHandle"]
        start_time = time.perf_counter()
        transaction_id = "unknown"

        try:
            body = json.loads(message["Body"])
            transaction_id = body.get("transaction_id", "unknown")
            correlation_id = body.get("correlation_id", str(uuid.uuid4()))

            set_correlation_id(correlation_id)
            logger.info(
                "async_post_processing_started",
                transaction_id=transaction_id,
                worker_id=self.worker_id,
            )

            # Step 1: Update account profile

            async with get_session() as session:
                profile_repo = AccountProfileRepository(session)
                await profile_repo.upsert_after_transaction(
                    account_id=body.get("sender_id", ""),
                    amount=Decimal(str(body.get("amount", 0))),
                    receiver_id=body.get("receiver_id", ""),
                device_fingerprint=body.get("device_fingerprint"),
                receiver_country=body.get("receiver_country"),
                decision=body.get("risk_decision", "REVIEW"),
                )
            
            if body.get("risk_decision") in ("BLOCK", "REVIEW"):
                try:
                    redis_client = get_redis()
                    failed_key = f"failed:1h:{body.get('sender_id', '')}"
                    await redis_client.incr(failed_key)
                    await redis_client.expire(failed_key, 3600)
                except Exception as e:
                    logger.warning("redis_failed_counter_error", error=str(e))

            # Step 2: Reconstruct RiskAssessment from SQS payload
            validated_factors = []
            for factor_data in body.get("risk_factors", []):
                try:
                    if isinstance(factor_data, dict):
                        validated_factors.append(RiskFactor(**factor_data))
                except Exception as e:
                    logger.warning(
                        "invalid_risk_factor_skipped",
                        factor=factor_data,
                        error=str(e),
                    )

            assessment = RiskAssessment(
                transaction_id=transaction_id,
                decision=body.get("risk_decision", "REVIEW"),
                risk_score=float(body.get("risk_score", 0.5)),
                risk_level=body.get("risk_level", "MEDIUM"),
                confidence=body.get("confidence", "MEDIUM"),
                risk_factors=validated_factors,
                processing_time_ms=float(body.get("processing_time_ms", 0)),
                model_version=body.get("model_version", "1.0.0"),
            )

            # Step 3: Persist RiskResult to DB (analyst fields start as NULL)
            async with get_session() as session:
                result_repo = RiskResultRepository(session)
                await result_repo.save(
                    assessment=assessment,
                    transaction_data=body,
                    rule_flags=body.get("rule_flags", []),
                    rule_score=float(body.get("rule_score", 0.0)),
                    ml_anomaly_score=float(body.get("ml_anomaly_score", 0.5)),
                    ml_model_version=body.get("ml_model_version", "unknown"),
                    ml_fallback_used=bool(body.get("ml_fallback_used", True)),
                    ml_features_used=body.get("ml_features_used"),
                    correlation_id=correlation_id,
                )

            # Step 4: Publish investigation trigger ONLY for BLOCK/REVIEW decisions.
            # APPROVE transactions are low-risk — no point burning Ollama compute on them.
            risk_decision = body.get("risk_decision", "REVIEW")
            if risk_decision in ("BLOCK", "REVIEW"):
                await self._publish_analyst_trigger(
                    transaction_id=transaction_id,
                    sender_id=body.get("sender_id", ""),
                    correlation_id=correlation_id,
                )
                logger.info(
                    "analyst_investigation_trigger_published",
                    transaction_id=transaction_id,
                    decision=risk_decision,
                )
            else:
                logger.info(
                    "analyst_investigation_skipped_low_risk",
                    transaction_id=transaction_id,
                    decision=risk_decision,
                )

            # Step 5: Publish RiskCompleted event
            await self._publish_completion(
                transaction_id=transaction_id,
                assessment=assessment,
                correlation_id=correlation_id,
            )

            # Step 6: Acknowledge message
            async with self._client() as client:
                await client.delete_message(
                    QueueUrl=self._queue_url,
                    ReceiptHandle=receipt_handle,
                )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "async_post_processing_completed",
                transaction_id=transaction_id,
                processing_time_ms=round(elapsed_ms, 2),
                worker_id=self.worker_id,
            )

        except Exception as e:
            logger.error(
                "message_processing_failed",
                transaction_id=transaction_id,
                error=str(e),
                message_id=message.get("MessageId"),
            )
            

        finally:
            clear_correlation_id()

    async def _publish_analyst_trigger(
        self,
        transaction_id: str,
        sender_id: str,
        correlation_id: str,
    ) -> None:
        """Publish a lightweight trigger to the analyst-service SQS queue."""
        payload = {
            "transaction_id": transaction_id,
            "sender_id": sender_id,
            "correlation_id": correlation_id,
        }
        try:
            async with self._client() as client:
                await client.send_message(
                    QueueUrl=self._analyst_queue_url,
                    MessageBody=json.dumps(payload),
                    MessageAttributes={
                        "EventType": {
                            "DataType": "String",
                            "StringValue": "AnalystInvestigationRequested",
                        }
                    },
                )
            logger.info("analyst_investigation_trigger_published", transaction_id=transaction_id)
        except Exception as e:
            logger.error("analyst_trigger_publish_failed", transaction_id=transaction_id, error=str(e))

    async def _publish_completion(
        self,
        transaction_id: str,
        assessment: RiskAssessment,
        correlation_id: str,
    ) -> None:
        """Publish RiskCompleted event for notification-service webhook."""
        payload = {
            "transaction_id": transaction_id,
            "decision": (
                assessment.decision.value
                if hasattr(assessment.decision, "value")
                else assessment.decision
            ),
            "risk_score": assessment.risk_score,
            "risk_level": (
                assessment.risk_level.value
                if hasattr(assessment.risk_level, "value")
                else assessment.risk_level
            ),
            "risk_factors": [rf.model_dump() for rf in assessment.risk_factors],
            # analyst_summary is written async by the analyst-service worker
            "correlation_id": correlation_id,
        }

        try:
            async with self._client() as client:
                await client.send_message(
                    QueueUrl=self._completed_queue_url,
                    MessageBody=json.dumps(payload, default=str),
                    MessageAttributes={
                        "EventType": {
                            "DataType": "String",
                            "StringValue": "RiskCompleted",
                        },
                        "TransactionId": {
                            "DataType": "String",
                            "StringValue": transaction_id,
                        },
                    },
                )
            logger.info(
                "risk_completed_event_published",
                transaction_id=transaction_id,
            )
        except Exception as e:
            logger.error(
                "completion_publish_failed",
                transaction_id=transaction_id,
                error=str(e),
            )
            