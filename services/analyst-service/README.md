# Aegis Risk: Analyst Service

The **Analyst Service** is the investigation and MLOps orchestration hub of the Aegis Risk microservices ecosystem. It provides two primary capabilities:

1.  **AI-Driven Fraud Investigation**: An asynchronous worker that performs deep-dive analysis of suspicious transactions using LLMs (e.g., Llama 3 via Ollama).
2.  **MLOps Orchestration**: A structured LlamaIndex Workflow that monitors model performance, decides when to retrain, and executes the retraining pipeline.

## Key Features

### 1. AI Analyst (Fraud Investigation)
When the **Risk Engine** identifies a transaction as `BLOCK` or `REVIEW`, it publishes a message to SQS. The `AnalystInvestigationWorker` picks this up and:
*   Queries historical transaction patterns for the user.
*   Uses a **ReAct Agent** to reason about the risk factors.
*   Generates a human-readable investigation report.
*   Writes the findings back to the `risk_results` database for the Bank Dashboard.

### 2. MLOps Retraining Workflow
The service implements a self-healing ML lifecycle using a **LlamaIndex Workflow**. This is a deterministic, event-driven pipeline:
*   **Performance Monitoring**: Queries the database for metrics (block rate, false positives, ML fallback frequency).
*   **Intelligent Decisioning**: An LLM analyzes the metrics to determine if a "Concept Drift" or "Data Drift" has occurred.
*   **Automated Retraining**: If retraining is approved, the workflow triggers an XGBoost training job on the latest data.
*   **Hot-Swapping**: Once the new model is validated, it signals the **ML Service** to reload the model via gRPC, ensuring zero-downtime updates.

## Technical Stack
*   **Language**: Python 3.12 (Poetry)
*   **Framework**: FastAPI (for gRPC health checks and internal monitoring)
*   **Orchestration**: LlamaIndex Workflows
*   **Messaging**: AWS SQS (polled via `aiobotocore`)
*   **Database**: PostgreSQL (shared with Risk Engine via SQLAlchemy)
*   **Communication**: gRPC (Server for synchronous investigations, Client for ML hot-swaps)

## Getting Started

### Environment Variables
Ensure the following are set in your `.env` or Docker Compose environment:
*   `ANALYST_SERVICE_GRPC_PORT`: Port for the gRPC server (default: `50056`).
*   `SQS_AGENT_INVESTIGATIONS_QUEUE`: SQS queue for incoming investigation requests.
*   `OLLAMA_BASE_URL`: URL for the Ollama inference server.

### Running Locally
```bash
# Install dependencies
poetry install

# Start the worker
poetry run python -m app.main
```

## Architecture Note
This service was renamed from `agentic-ai-service` to **Analyst Service** to better reflect its dual role as a fraud investigator and a machine learning analyst.
