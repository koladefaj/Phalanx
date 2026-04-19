"""ML Service — gRPC server entrypoint."""

import asyncio
from concurrent import futures

import grpc

from aegis_shared.generated import ml_service_pb2_grpc
from aegis_shared.utils.logging import setup_logger

from app.config import settings
from app.core.predictor import RiskPredictor
from app.grpc.server.servicer import MLServicer
from app.grpc.server.setup import create_grpc_server

logger = setup_logger("ml-service", settings.LOG_LEVEL)


async def serve():
    """Start the ML gRPC server."""

    # Initialize the ONNX predictor singleton (loads model into memory once)
    predictor = RiskPredictor()

    logger.info("predictor_loaded", model_path=settings.MODEL_PATH)

    # Create gRPC server
    server = create_grpc_server()

    # Register servicer
    servicer = MLServicer(predictor)
    ml_service_pb2_grpc.add_MLServiceServicer_to_server(servicer, server)

    listen_addr = f"0.0.0.0:{settings.ML_SERVICE_GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("ml_service_starting", address=listen_addr)
    await server.start()
    logger.info("ml_service_started", address=listen_addr)

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("ml_service_keyboard_interrupt_received")
    finally:
        logger.info("ml_service_shutting_down")
        await server.stop(grace=5)
        logger.info("ml_service_stopped")


if __name__ == "__main__":
    asyncio.run(serve())
