"""Analyst Service — gRPC server + SQS worker entrypoint."""

import asyncio
import sys
import grpc
from app.config import settings
from app.db.session import engine
from app.grpc.server.setup import create_grpc_server
from app.grpc.server.servicer import AnalystServicer
from app.services.llama_agent import LlamaIndexAgentService
from app.queue.sqs_consumer import AnalystInvestigationWorker
from app.queue.mlops_consumer import MLOpsWorker
from aegis_shared.utils.logging import setup_logger
from aegis_shared.utils.sqs import init_boto_session
from aegis_shared.generated import analyst_service_pb2_grpc

logger = setup_logger("analyst-service", "INFO")


async def serve():
    """Start the Analyst gRPC server and SQS investigation worker."""

    logger.info("Initializing Analyst Service...")

    # Bootstrap shared AWS session (needed by the SQS worker)
    try:
        await init_boto_session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
    except Exception as e:
        logger.error("startup_sqs_init_failed", error=str(e))
        raise

    # Initialize the core agent service (shared by gRPC servicer AND SQS worker)
    try:
        agent_service = LlamaIndexAgentService()
    except Exception as e:
        logger.error("startup_agent_init_failed", error=str(e))
        sys.exit(1)

    # ── gRPC server ───────────────────────────────────────────────────────────
    server = create_grpc_server()
    servicer = AnalystServicer(agent_service)
    analyst_service_pb2_grpc.add_AnalystServiceServicer_to_server(servicer, server)

    listen_addr = f"0.0.0.0:{settings.ANALYST_SERVICE_GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("analyst_service_starting", address=listen_addr)
    await server.start()
    logger.info("analyst_service_started", address=listen_addr)

    # ── SQS workers ───────────────────────────────────────────────────────────
    shutdown_event = asyncio.Event()
    agent_worker  = AnalystInvestigationWorker(agent=agent_service)
    mlops_worker  = MLOpsWorker()

    try:
        # All three run concurrently: gRPC server + fraud investigation worker
        # + MLOps retrain worker. If any crashes, the others keep running.
        await asyncio.gather(
            server.wait_for_termination(),
            agent_worker.run(shutdown_event),
            mlops_worker.run(shutdown_event),
        )
    except KeyboardInterrupt:
        logger.info("analyst_service_keyboard_interrupt_received")
    finally:
        logger.info("analyst_service_shutting_down")
        shutdown_event.set()        # signal worker to stop
        await server.stop(grace=5)  # finish in-flight RPCs
        await engine.dispose()      # close DB connection pool
        logger.info("analyst_service_stopped")


if __name__ == "__main__":
    asyncio.run(serve())
