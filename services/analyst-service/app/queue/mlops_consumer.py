"""MLOps SQS consumer — listens for retrain trigger messages.

Message schema on aegis-model-retrain-requests:
    {
      "trigger": "manual" | "scheduled",
      "lookback_days": 7,          # optional, default 7
      "correlation_id": "uuid"     # optional
    }

The consumer starts the RetrainingWorkflow and logs the final result.
It uses the same acks_late pattern as the agent investigation worker.
"""

import asyncio
import json
import uuid

from aegis_shared.utils.sqs import get_boto_session
from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.tracing import set_correlation_id, clear_correlation_id
from app.config import settings
from app.workflows.retrain_workflow import RetrainingWorkflow
from llama_index.core.workflow import StartEvent

logger = get_logger("mlops_worker")


class MLOpsWorker:
    """
    SQS consumer that triggers the RetrainingWorkflow.

    Designed to run alongside the AgentInvestigationWorker in the same
    asyncio.gather() call — both workers run concurrently in one process.
    """

    def __init__(self) -> None:
        self.session = get_boto_session()
        self._queue_url: str | None = None
        self.worker_id = settings.WORKER_ID.replace("agent", "mlops")

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
        async with self._client() as client:
            try:
                resp = await client.get_queue_url(QueueName=settings.SQS_RETRAIN_QUEUE)
                self._queue_url = resp["QueueUrl"]
            except client.exceptions.QueueDoesNotExist:
                # Auto-create on first boot — avoids needing LocalStack to be
                # pre-provisioned before this service starts.
                resp = await client.create_queue(
                    QueueName=settings.SQS_RETRAIN_QUEUE,
                    Attributes={"VisibilityTimeout": "600"},
                )
                self._queue_url = resp["QueueUrl"]
                logger.info("mlops_queue_created", queue=self._queue_url)
        return self._queue_url

    async def run(self, shutdown_event: asyncio.Event) -> None:
        queue_url = await self._get_queue_url()
        logger.info("mlops_worker_started", worker_id=self.worker_id, queue=queue_url)

        while not shutdown_event.is_set():
            try:
                await self._poll(queue_url)
            except Exception as e:
                logger.error("mlops_worker_poll_error", error=str(e))
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

        logger.info("mlops_worker_stopped", worker_id=self.worker_id)

    async def _poll(self, queue_url: str) -> None:
        async with self._client() as client:
            response = await client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,   # retrain is heavy — never batch
                WaitTimeSeconds=5,
            )

        for msg in response.get("Messages", []):
            await self._process(msg, queue_url)

    async def _process(self, message: dict, queue_url: str) -> None:
        receipt_handle = message["ReceiptHandle"]
        try:
            body = json.loads(message["Body"])
            correlation_id = body.get("correlation_id", str(uuid.uuid4()))
            lookback_days = int(body.get("lookback_days", 7))
            trigger = body.get("trigger", "unknown")

            set_correlation_id(correlation_id)
            logger.info(
                "mlops_retrain_triggered",
                trigger=trigger,
                lookback_days=lookback_days,
                correlation_id=correlation_id,
            )

            # Run the workflow — timeout generous for LLM + XGBoost training
            workflow = RetrainingWorkflow(timeout=600)
            result = await workflow.run(
                startEvent=StartEvent(lookback_days=lookback_days)
            )

            logger.info("mlops_workflow_complete", result=str(result)[:300])

            # acks_late — only delete after successful completion
            async with self._client() as client:
                await client.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=receipt_handle
                )

        except Exception as e:
            logger.error("mlops_workflow_failed", error=str(e))
            # Don't delete — let SQS redeliver
        finally:
            clear_correlation_id()


async def trigger_retrain_now(lookback_days: int = 7) -> dict:
    """
    Programmatic trigger — used by the API endpoint for manual kicks.
    Runs the workflow directly in-process (no SQS round-trip needed).
    """
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)

    logger.info("manual_retrain_triggered", correlation_id=correlation_id)

    try:
        workflow = RetrainingWorkflow(timeout=600)
        result = await workflow.run(
            startEvent=StartEvent(lookback_days=lookback_days)
        )
        return {
            "status": "completed",
            "correlation_id": correlation_id,
            "result": str(result),
        }
    except Exception as e:
        logger.error("manual_retrain_failed", error=str(e), correlation_id=correlation_id)
        return {"status": "failed", "correlation_id": correlation_id, "error": str(e)}
    finally:
        clear_correlation_id()
