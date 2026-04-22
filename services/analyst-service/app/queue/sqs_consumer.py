"""AnalystInvestigationWorker — SQS consumer for the analyst-service.

This worker implements the acks_late pattern:
  - Poll     : receive message from aegis-agent-investigations
  - Process  : run the full AI analyst investigation
  - Write    : persist analyst_summary and related fields to risk_results DB
  - Delete   : only then acknowledge (delete) the SQS message

If the analyst fails or the LLM is unavailable:
  - The message is NOT deleted.
  - SQS visibility timeout (180 s) expires → message becomes visible again.
  - After WORKER_MAX_RETRIES local retries on top of the SQS redelivery,
    the message is moved to the DLQ (aegis-agent-investigations-dlq).
"""

import asyncio
import json
import time
import uuid
from typing import Optional

from aegis_shared.utils.sqs import get_boto_session
from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.tracing import set_correlation_id, clear_correlation_id
from app.config import settings
from app.db.session import get_session
from app.repositories.risk_result_repo import AnalystRiskResultRepository
from app.services.base import BaseAgentService

logger = get_logger("analyst_investigation_worker")


class AnalystInvestigationWorker:
    """SQS consumer that drives AI fraud investigations.

    Message schema expected on aegis-agent-investigations:
        {
          "transaction_id": "uuid-string",
          "sender_id":      "acct-001",
          "correlation_id": "trace-uuid"
        }
    """

    def __init__(self, agent: BaseAgentService) -> None:
        self.agent = agent
        self.session = get_boto_session()
        self._queue_url: Optional[str] = None
        self.worker_id = settings.WORKER_ID

    # ── SQS helpers ──────────────────────────────────────────────────────────

    def _client(self):
        return self.session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        )

    async def _get_queue_url(self) -> str:
        if self._queue_url:
            return self._queue_url
        try:
            async with self._client() as client:
                response = await client.get_queue_url(
                    QueueName=settings.SQS_AGENT_INVESTIGATIONS_QUEUE
                )
                self._queue_url = response["QueueUrl"]
                return self._queue_url
        except Exception:
            # Fallback for LocalStack
            self._queue_url = (
                f"{settings.AWS_ENDPOINT_URL}/000000000000/"
                f"{settings.SQS_AGENT_INVESTIGATIONS_QUEUE}"
            )
            return self._queue_url

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self, shutdown_event: asyncio.Event) -> None:
        queue_url = await self._get_queue_url()
        logger.info("analyst_worker_started", worker_id=self.worker_id, queue=queue_url)

        while not shutdown_event.is_set():
            try:
                await self._poll_messages(queue_url)
            except Exception as e:
                logger.error("analyst_worker_poll_error", error=str(e))
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

        logger.info("analyst_worker_stopped", worker_id=self.worker_id)

    async def _poll_messages(self, queue_url: str) -> None:
        async with self._client() as client:
            response = await client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=settings.WORKER_MAX_MESSAGES,
                # Do NOT set VisibilityTimeout here — it is set on the queue itself (180 s).
                # This means if we crash mid-processing, SQS automatically
                # re-delivers after the window without us doing anything.
                WaitTimeSeconds=5,
                MessageAttributeNames=["All"],
                AttributeNames=["ApproximateReceiveCount"],
            )

        messages = response.get("Messages", [])
        if not messages:
            return

        logger.info("analyst_messages_received", count=len(messages))

        # Process messages CONCURRENTLY within the batch.
        # Each investigation is I/O-heavy (LLM call + DB write), so asyncio
        # can interleave them without blocking the event loop.
        # NOTE: If the local LLM is single-threaded, this won't parallelize the LLM
        # compute itself, but it DOES parallelize DB reads/writes and network I/O.
        await asyncio.gather(
            *[self._process_message(msg, queue_url) for msg in messages],
            return_exceptions=True,  # don't let one failure cancel the others
        )

    # ── Per-message processing ─────────────────────────────────────────────────

    async def _process_message(self, message: dict, queue_url: str) -> None:
        receipt_handle = message["ReceiptHandle"]
        transaction_id = "unknown"
        start_time = time.perf_counter()

        # Extract SQS delivery count for local retry guard
        attrs = message.get("Attributes", {})
        receive_count = int(attrs.get("ApproximateReceiveCount", 1))

        if receive_count > settings.WORKER_MAX_RETRIES:
            logger.warning(
                "agent_max_retries_exceeded_dropping",
                transaction_id=transaction_id,
                receive_count=receive_count,
                max_retries=settings.WORKER_MAX_RETRIES,
            )
            # Still delete — the DLQ already has it from SQS redrive.
            await self._delete_message(queue_url, receipt_handle)
            return

        try:
            body = json.loads(message["Body"])
            transaction_id = body.get("transaction_id", "unknown")
            sender_id = body.get("sender_id", "")
            correlation_id = body.get("correlation_id", str(uuid.uuid4()))

            set_correlation_id(correlation_id)
            logger.info(
                "analyst_investigation_started",
                transaction_id=transaction_id,
                sender_id=sender_id,
                receive_count=receive_count,
                worker_id=self.worker_id,
            )

            # ── Idempotency guard ────────────────────────────────────────────
            # If the agent already ran for this transaction (e.g. duplicate
            # delivery after a partial failure), skip processing.
            async with get_session() as session:
                repo = AnalystRiskResultRepository(session)
                if await repo.is_already_investigated(transaction_id):
                    logger.info(
                        "analyst_investigation_skipped_already_done",
                        transaction_id=transaction_id,
                    )
                    await self._delete_message(queue_url, receipt_handle)
                    return

            # ── Run the analyst ─────────────────────────────────────────────────
            report = await self.agent.investigate_transaction(
                transaction_id=transaction_id,
                sender_id=sender_id,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # ── Parse the report (best-effort) ────────────────────────────────
            parsed = self._parse_report(report)

            # ── Write back to DB ──────────────────────────────────────────────
            async with get_session() as session:
                repo = AnalystRiskResultRepository(session)
                await repo.update_analyst_investigation(
                    transaction_id=transaction_id,
                    agent_summary=parsed["summary"],
                    agent_risk_factors=parsed["risk_factors"],
                    agent_recommendation=parsed["recommendation"],
                    agent_confidence=parsed["confidence"],
                    agent_model=self.agent.get_agent_name(),
                    agent_latency_ms=elapsed_ms,
                    agent_fallback_used=False,
                )

            # ── acks_late: only delete AFTER successful write ─────────────────
            await self._delete_message(queue_url, receipt_handle)

            logger.info(
                "analyst_investigation_completed",
                transaction_id=transaction_id,
                verdict=parsed["verdict"],
                latency_ms=round(elapsed_ms, 2),
            )

        except Exception as e:
            logger.error(
                "analyst_investigation_failed",
                transaction_id=transaction_id,
                error=str(e),
                receive_count=receive_count,
            )
            # Do NOT delete — let visibility timeout expire so SQS redelivers.

        finally:
            clear_correlation_id()

    async def _delete_message(self, queue_url: str, receipt_handle: str) -> None:
        async with self._client() as client:
            await client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )

    # ── Report parsing ─────────────────────────────────────────────────────────

    @staticmethod
    def _parse_report(raw: str) -> dict:
        """Best-effort extraction of structured fields from the agent's raw text."""
        import re

        verdict = "SUSPICIOUS"
        for v in ("FRAUDULENT", "LEGITIMATE", "SUSPICIOUS"):
            if v in raw.upper():
                verdict = v
                break

        confidence_map = {"HIGH": 0.9, "MEDIUM": 0.65, "LOW": 0.35}
        confidence = 0.65
        for label, val in confidence_map.items():
            if label in raw.upper():
                confidence = val
                break

        recommendation = "REVIEW"
        for r in ("BLOCK", "ALLOW", "REVIEW"):
            if r in raw.upper():
                recommendation = r
                break

        # Extract bullet-point risk factors if present (must be at start of line)
        risk_factors = re.findall(r"^\s*[-*]\s*(.+)", raw, re.MULTILINE)
        if not risk_factors:
            risk_factors = [verdict.lower().replace("_", " ")]

        # Extract summary if the LLM followed instructions
        summary_match = re.search(r"SUMMARY:\s*(.*?)(?=\n[A-Z]+:|$)", raw, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
        else:
            summary = raw.replace("\n", " ")

        return {
            "summary": summary,
            "verdict": verdict,
            "confidence": confidence,
            "recommendation": recommendation,
            "risk_factors": risk_factors[:10],  # cap at 10
        }
