# Phalanx - Risk Engine

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![gRPC](https://img.shields.io/badge/gRPC-Protobuf-blueviolet?logo=google&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![ML](https://img.shields.io/badge/ML-XGBoost_→_ONNX-FF6600)
![License](https://img.shields.io/badge/License-MIT-green)

> Production-grade real-time fraud detection platform. Evaluates every inbound transaction against a hybrid rules + ML ensemble, returns a deterministic **APPROVE / REVIEW / BLOCK** verdict in **< 200ms P95**, and triggers an async AI investigation for flagged cases.

---

## The Problem

Fraud detection for fintech businesses has a well-known tension: **accuracy vs. latency**.

- **Pure rule engines** are deterministic and auditable, but brittle — rules written for known fraud patterns miss novel ones.
- **Pure ML models** adapt over time, but are opaque, slow to deploy, and unreliable on new accounts with little history.
- **Combining both** in a sub-200ms synchronous pipeline, while keeping each layer independently evolvable and the full audit trail intact, is the hard engineering problem.

Layered on top: **multi-tenancy** (every byte of data must be tenant-scoped at the schema level), **idempotency** (payment clients retry; the database must never double-process), and **zero-downtime model updates** (fraud patterns shift; retraining can't drop a single live connection).

Aegis Risk solves this stack. It is designed as a portfolio piece demonstrating production-grade distributed systems engineering — not a tutorial.

---

## Architecture

```
  B2B Client ──REST/JWT──► API Gateway (:8000)
                                │          Redis: rate limiting, idempotency cache
                             gRPC │
                                ▼
                    Transaction Service (:50051)
                       Postgres: transaction ledger
                                │
                             gRPC │  ~2ms round-trip
                                ▼
                      Risk Engine (:50052)
                         Redis:  profile cache (30s TTL), velocity counters
                         Postgres: account profiles
                                │
                             gRPC │  ~1.7ms round-trip
                                ▼
                       ML Service (:50053)
                          ONNX/XGBoost: 0.4–0.8ms per prediction

    ◄── APPROVE / REVIEW / BLOCK verdict returned (<200ms P95) ──►

                                │
                             SQS │  async, non-blocking
                                ▼
          Risk Engine Worker (SQS consumer)
            ├─► upsert account profile + invalidate Redis cache
            ├─► persist full RiskResult to Postgres
            ├─► Analyst Service (:50056) — LlamaIndex ReAct + instructor
            │     (BLOCK/REVIEW only — APPROVE skips the LLM entirely)
            └─► Notification Service (:50055) — HMAC-signed webhooks
```

**API Surface**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions` | Submit transaction for risk evaluation |
| `GET` | `/transactions/{id}` | Retrieve result + analyst investigation |
| `POST` | `/transactions/{id}/reinvestigate` | Re-trigger LLM investigation (analyst role) |
| `POST` | `/mlops/reload-model` | Hot-swap ONNX model from S3 (admin role) |
| `GET` | `/health` | Stack liveness check |

---

## ⚡ Performance

Measured against a local Docker Compose stack (single machine, no network hops between services).

### End-to-End Latency (POST /transactions)

| Scenario | P50 | P95 |
|----------|-----|-----|
| Warm, single request | ~100ms | ~200ms |
| Warm, 20 concurrent (same account) | ~200ms | ~280ms |
| Cold start (first request after restart) | ~640ms | — |

Cold-start latency is dominated by gRPC channel establishment; subsequent requests are unaffected.

### Internal Pipeline Breakdown (warm, single request)

| Stage | Time |
|-------|------|
| Idempotency check (Redis + DB SELECT) | ~10–20ms |
| gRPC hop: transaction-service → risk-engine | ~2ms |
| Account profile load (Redis cache hit) | <1ms |
| Account profile load (DB miss, first request) | ~20–30ms |
| Rules evaluation (8 rules, in-process) | <1ms |
| ML scoring (ONNX inference) | 0.4–0.8ms |
| ML gRPC round-trip (transaction → ml-service) | ~1.7ms |
| Risk engine total (rules + ML + scoring) | 20–28ms |
| DB INSERT with final status | ~30–50ms |
| SQS event publish | ~15ms |
| gRPC return hop | ~2ms |

The account profile is cached in Redis (30s TTL) after the first DB load. Under concurrent load from the same sender, all parallel requests after the first serve the profile from cache — the main reason P95 holds under 20-concurrent.

### ML Service

| Metric | Value |
|--------|-------|
| ONNX inference latency | 0.4–0.8ms |
| gRPC round-trip (docker bridge) | ~1.7ms |
| Model | XGBoost → ONNX, 20-feature behavioural vector |
| ML contribution to wall-clock time | < 2% |
| Hot-swap (S3 → in-memory, zero connections dropped) | supported |

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **API / Transport** | FastAPI, gRPC (HTTP/2 + Protobuf), REST |
| **Language** | Python 3.12 (async/await throughout) |
| **Databases** | PostgreSQL 18 (asyncpg + SQLAlchemy async ORM), Redis 7 |
| **ML / Inference** | XGBoost trained model → ONNX Runtime (sub-ms inference, GIL-free) |
| **AI / LLM** | LlamaIndex ReActAgent + instructor (structured extraction) |
| **LLM Providers** | Anthropic Claude, OpenAI GPT, Google Gemini, Ollama (local) |
| **Queue / Events** | AWS SQS (LocalStack in dev), acks-late pattern |
| **Auth** | AWS Cognito (RS256 JWT), Lambda-triggered RBAC |
| **Infra** | Docker Compose, LocalStack, Alembic migrations |
| **Observability** | structlog (structured JSON), correlation ID tracing across all services |

---

## ✨ What Makes This Production-Quality

- **Sub-200ms fraud decisions** — P95 ~200ms warm under 20 concurrent requests; full pipeline breakdown [in the Performance section](#-performance)
- **Single-write commit path** — transaction UUID generated upfront, risk scored outside DB, single INSERT at final status; eliminates a round-trip DB UPDATE from the hot path
- **Account profile Redis cache** — 30s TTL cache on behavioural profiles; SQS worker invalidates after each upsert so warm senders skip the Postgres round-trip entirely
- **Concurrent Redis operations** — all 4 velocity/burst reads run via `asyncio.gather`; TTL refreshes are fire-and-forget tasks off the critical path
- **Rules-first 70/30 ensemble** — deterministic rule engine governs 70% of the score; ML refines, never overrides; prevents regulatory drift and false positives on new accounts
- **ONNX ML inference at 0.4–0.8ms** — XGBoost exported to ONNX Runtime; bypasses the Python GIL, delivers sub-ms predictions with a ~1.7ms gRPC round-trip
- **Zero-downtime ML hot-swap** — admin triggers `POST /mlops/reload-model`; ML service acquires a thread lock, pulls new ONNX binary from S3, atomically swaps the inference session with no TCP connections dropped
- **Two-phase LLM investigation** — Phase 1: LlamaIndex ReActAgent reasons with 4 internal tools; Phase 2: instructor extracts a validated `FraudInvestigationReport` Pydantic model; typed fields, auto-retry on schema failure, no regex
- **Provider-agnostic LLM factory** — swap Ollama ↔ Claude ↔ GPT ↔ Gemini with two `.env` changes; zero code changes
- **Acks-late SQS pattern** — messages deleted only after all downstream writes complete; worker crash → message reappears after visibility timeout, zero data loss
- **Multi-tenant isolation** — Cognito `custom:tenant_id` claim flows through every gRPC hop as `client_id`; every DB query is tenant-scoped; three separate databases enforce ownership boundaries at the schema level
- **Double-checked locking idempotency** — Redis `SET NX` distributed lock + double-check + DB `UNIQUE` constraint; prevents thundering herd on retry storms without expensive serialized DB writes

---

## 🔑 Key Engineering Decisions

| Decision | What We Chose | What We Didn't | Why |
|----------|--------------|----------------|-----|
| Internal transport | gRPC / Protobuf | REST / JSON | HTTP/2 multiplexing + binary encoding → <2ms round-trips; strong typing caught the `ml_score` mapper gap at compile-time |
| ML inference format | ONNX Runtime | XGBoost native / scikit-learn | GIL-free C++ execution: 0.4–0.8ms vs ~5ms; safe to call from async without blocking the event loop |
| Async messaging | AWS SQS | Kafka | SQS acks-late gives at-least-once delivery with near-zero ops; Kafka's offset management would add operational overhead for our single-consumer use case |
| Auth & RBAC | Cognito RS256 JWT + Lambda trigger | Custom JWT / API keys | Offloads key rotation and JWKS; `custom:tenant_id` claim in the token carries multi-tenancy without an extra DB lookup |
| Idempotency | Redis `NX` lock + DB `UNIQUE` | DB `UNIQUE` alone | Redis absorbs the thundering-herd retry storm before it touches Postgres; DB constraint is the final backstop, not the first line |
| DB commit path | Pre-generate UUID, single INSERT | `RECEIVED` → `UPDATE` | Eliminates one full DB session from the hot path; no partial state in the ledger |
| LLM integration | LlamaIndex + instructor | Raw API calls / LangChain | ReAct agent enables multi-tool reasoning over internal data; instructor enforces Pydantic schema with auto-retry — no regex post-processing |
| Profile cache TTL | 30 seconds | No cache / longer TTL | 30s absorbs concurrent-request bursts from the same sender; short enough that `is_high_risk` flag staleness is tolerable within one SQS processing cycle |

---

## 📁 Project Structure

```
aegis-risk/
├── proto/                          # Protobuf definitions — source of truth for all service contracts
│   ├── common.proto
│   ├── transaction.proto
│   ├── risk_engine.proto
│   ├── ml_service.proto
│   ├── analyst_service.proto
│   └── notification.proto
├── shared/aegis_shared/            # Installable shared library; imported by all six services
│   ├── enums.py                    # RiskDecision, RiskLevel, TransactionStatus
│   ├── exceptions.py
│   ├── schemas/                    # Pydantic models (risk, transaction, common)
│   ├── generated/                  # Compiled protobuf stubs (auto-generated, do not edit)
│   ├── grpc/interceptors/          # Correlation ID propagation across gRPC hops
│   └── utils/                      # logging, tracing, redis, sqs helpers
├── services/
│   ├── api-gateway/                # FastAPI REST, JWT validation, rate limiting
│   ├── transaction-service/        # gRPC server, transaction ledger, idempotency
│   ├── risk-engine-service/        # Rules engine, ML ensemble, SQS worker
│   ├── ml-service/                 # ONNX inference server, hot-swap endpoint
│   ├── analyst-service/            # LLM investigation (ReAct), MLOps workflow
│   └── notification-service/       # Webhook delivery, HMAC signing
├── infra/
│   ├── localstack-init.sh          # SQS queue bootstrap for local dev
│   ├── init-databases.sql          # Three-database setup (transactions / risk / analytics)
│   └── fix_proto_imports.py        # Rewrites bare proto imports to package-relative after make proto
├── tests/
│   └── integration/                # End-to-end tests against the running Docker stack
│       ├── conftest.py
│       └── test_transactions.py
├── docker-compose.yml
├── Makefile                        # make proto, make up, make build, make seed
└── generate_seed_data.py           # Generates 6-month SQL seed for test personas
```

---

## 🔒 Security

| Threat | Control | Implementation |
|--------|---------|----------------|
| Unauthorized API access | RS256 JWT (Cognito JWKS) | `middleware/auth/cognito.py`; JWKS cached, fail-secure on unavailability |
| Cross-tenant data leak | `client_id` column filter on every query | Three separate databases; every repo method accepts `client_id` |
| Idempotency replay attack | 24h Redis cache + DB `UNIQUE` | `SET NX` distributed lock → double-check → constraint backstop |
| Thundering herd (retry storm) | Redis distributed lock | One worker processes each idempotency key; concurrent duplicates served from cache |
| API abuse / DDoS | Sliding-window rate limit | 100 req/60s per client via Redis; enforced in api-gateway before gRPC dispatch |
| Webhook spoofing | HMAC-SHA256 signature | `X-Aegis-Signature` header on every outbound webhook; client verifies with shared secret |
| Model poisoning via hot-swap | Admin JWT required | `POST /mlops/reload-model` requires `admin` scope; S3 pull uses IAM credentials |
| Role escalation | Cognito Lambda post-confirmation trigger | On registration, Lambda inspects email domain → auto-assigns `admin` / `analyst` / `client` |

**Serverless RBAC — how it works:**
On user registration, a Cognito Post-Confirmation Lambda inspects the email domain and calls `admin_add_user_to_group`. `@aegisrisk.internal` → `admin`, `@analyst.aegisrisk.internal` → `analyst`, everything else → `client`. No manual permission assignment.

```python
# Cognito Post-Confirmation Trigger
def lambda_handler(event, context):
    import boto3
    client = boto3.client('cognito-idp', region_name=event.get('region', 'eu-west-2'))
    email = event['request']['userAttributes'].get('email', '')
    if email.endswith('@aegisrisk.internal'):
        group = 'admin'
    elif email.endswith('@analyst.aegisrisk.internal'):
        group = 'analyst'
    else:
        group = 'client'
    client.admin_add_user_to_group(
        UserPoolId=event['userPoolId'],
        Username=event['userName'],
        GroupName=group
    )
    return event
```

**Manual User Bootstrapping (for Testing)**
```bash
aws cognito-idp admin-create-user \
    --user-pool-id <POOL_ID> \
    --username test_admin \
    --user-attributes Name=email,Value=test@aegisrisk.internal Name=email_verified,Value=true \
    --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
    --user-pool-id <POOL_ID> \
    --username test_admin \
    --password "AegisTest123!" \
    --permanent
```

---

## 🧪 Testing

### Running Integration Tests

Tests run against the full Docker Compose stack — no mocks.

```bash
# 1. Start the stack
docker compose up -d

# 2. Seed the database
python generate_seed_data.py
cat seed_data.sql | docker exec -i aegis-risk-postgres-1 psql -U aegis

# 3. Install test dependencies and run
pip install pytest httpx
pytest tests/integration/ -v
```

Set `AEGIS_BASE_URL` to override the default `http://localhost:8000`.

### Why Integration Tests Instead of Unit Mocks?

The most valuable bugs in this system live at **service boundaries**: the gRPC proto field mapping, the Redis key naming, the SQS payload shape. Unit tests with mocked gRPC stubs would pass even when those contracts are broken. All three of the bugs found during development were boundary bugs that mocks would have hidden:

1. `ml_score: 0.0` in REST response — `from_evaluate_proto()` in `transaction-service/mappers/client_mapper.py` copied `rule_score` but never copied `ml_score`; passed in all unit tests because the mapper was never called against a real proto
2. `ml_anomaly_score: 0.0` in the DB — hardcoded in the SQS event payload; only visible by querying the actual database
3. Redis velocity counter not being read — key naming mismatch only visible when Redis is actually running

### Test Coverage

| Test | What it verifies |
|------|-----------------|
| `test_response_has_required_fields` | All expected fields present and typed correctly |
| `test_ml_score_propagated` | `ml_score` > 0 for established account (catches mapper gaps) |
| `test_low_risk_sender_approved` | Seeded clean sender + known device → `APPROVE`, `risk_score` < 0.5 |
| `test_high_risk_blocked` | New account + $14.5k + GB→RU corridor + unknown device → `BLOCK` |
| `test_risk_factors_present_for_flagged` | Flagged transactions have at least one `risk_factor` explaining the decision |
| `test_duplicate_key_returns_same_result` | Same payload submitted twice → second has `already_existed: true`, same `transaction_id` |
| `test_duplicate_key_different_amount_rejected` | Same key, different amount → `409 Conflict` |
| `test_velocity_spike_triggers_review` | 5 cross-border transactions from fresh sender → 5th trips velocity+geo rules into `REVIEW` |
| `test_warm_request_under_500ms` | Warm request completes in < 500ms end-to-end |
| `test_health_endpoint` | Stack is up and responding |

---

## 🚀 Quickstart (Running Locally)

Aegis Risk is fully containerized. You can spin up the entire microservice ecosystem, including local mocks for AWS (LocalStack), Postgres, and Redis, using a single command.

### 1. Prerequisites
- **Docker** & **Docker Compose**
- **An LLM provider** — the Analyst Service is provider-agnostic. Choose one:
  - **Ollama** (default, free, runs locally) — install from [ollama.com](https://ollama.com) and pull a model: `ollama pull gemma3:4b`
  - **Anthropic** — set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` in `.env`
  - **OpenAI** — set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` in `.env`
  - **Google Gemini** — set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` in `.env`

### 2. Bootstrapping the Environment
Clone the repository and spin up the infrastructure:
```bash
docker compose up -d --build
```

### 3. Seeding the Database
To avoid cold-start issues with the ML models and to establish historical profiles for our test personas, generate and inject the seed data:
```bash
python generate_seed_data.py
cat seed_data.sql | docker exec -i aegis-risk-postgres-1 psql -U aegis
```

### 4. Configuring AWS Cognito (Optional)
By default, the `.env` uses LocalStack for AWS services. However, Aegis Risk relies heavily on **AWS Cognito** for Multi-Tenancy (via `custom:tenant_id` claims) and Role-Based Access Control (RBAC). 

If you wish to attach your own real AWS Cognito User Pool:
1. Create a Cognito User Pool with a custom attribute named `custom:tenant_id`.
2. Create an App Client and ensure it has **Read Access** to `custom:tenant_id`.
3. Update your `.env` file with your real AWS credentials and Cognito details:
```env
AWS_ENDPOINT_URL= # Leave blank to bypass LocalStack
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXX
COGNITO_APP_CLIENT_ID=your_client_id
COGNITO_APP_CLIENT_SECRET=your_client_secret
COGNITO_DOMAIN=https://your-domain.auth.us-east-1.amazoncognito.com
```

### 5. Accessing the APIs
- **API Gateway (Swagger UI):** `http://localhost:8000/docs`
- **Authentication:** To get a valid JWT, visit `http://localhost:8000/auth/login`. This will execute the OAuth2 flow and return an ID token with the necessary `profile` scopes and tenant mapping.

### 6. Local Dev: Skip Cognito Auth
For fast local testing without setting up Cognito, set `DEV_BYPASS_AUTH=true` in `.env`. Then pass your tenant ID directly via header — no JWT required:

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "X-Dev-Tenant-Id: 56f292e4-80f1-704a-38f4-42f883cf5d91" \
  -d '{"idempotency_key": "test-001", "amount": 250.00, ...}'
```

> This flag has no effect if `ENVIRONMENT=production` — it is a development-only shortcut.

---

## 🤖 Configuring the AI Analyst

The Analyst Service is fully LLM-agnostic. Switch providers by changing two variables in `.env` — no code changes, no rebuild required beyond `docker compose up --build`.

### Supported Providers

| Provider | `LLM_PROVIDER` | Recommended Model | Key Required |
|----------|---------------|-------------------|--------------|
| Ollama (local) | `ollama` | `gemma3:4b` | No |
| Anthropic Claude | `anthropic` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Google Gemini | `gemini` | `models/gemini-2.0-flash` | `GEMINI_API_KEY` |

### Example: Switch to Claude

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Example: Switch to OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...
```

### Example: Switch to Gemini

```env
LLM_PROVIDER=gemini
LLM_MODEL=models/gemini-2.0-flash
GEMINI_API_KEY=AIzaSy...
```

### Ollama (Default — No API Key)

Ollama runs a local model on your host machine. The Docker container reaches it via `host.docker.internal`.

```bash
ollama pull gemma3:4b       # fast, 4B params
ollama pull gemma3:12b      # better quality, 12B params
ollama pull llama3.1:latest # Meta Llama 3.1 8B
```

```env
LLM_PROVIDER=ollama
LLM_MODEL=gemma3:4b
LLM_BASE_URL=http://host.docker.internal:11434
```

> **Note:** The AI investigation only fires for `BLOCK` and `REVIEW` decisions — `APPROVE` transactions skip the LLM entirely to minimise cost and latency.

---

## 🏛 Service Deep-Dive

### 1. API Gateway (`api-gateway`)
The edge of the network. It handles all Internet-facing interactions over REST HTTP.
- **Edge Security**: Exposes public REST API endpoints (`/transactions`, `/auth`) built in `FastAPI`.
- **JWT & Rate Limiting**: Intercepts requests to validate asymmetric JWT access tokens from AWS Cognito and enforces strict rate limiting decoupled via `Redis`.
- **gRPC Translation**: Validates incoming JSON structures using Pydantic, instantly translating them into strictly typed Protobuf messages and dispatching them to the internal subnet via high-speed gRPC Channels.

### 2. Transaction Service (`transaction-service`)
The system's mission-critical ledger ingress and data harmonization layer.
- **Single-Write Commit Path**: Generates a `transaction_id` upfront, scores risk outside any DB session, then commits a single INSERT directly into the final status (`APPROVED`/`REVIEW`/`BLOCKED`). There is no intermediate `RECEIVED → final` UPDATE step — this eliminates one full DB session from the hot path.
- **Strict Two-Way Idempotency**:
  - **Ingress Safety (Redis + DB Constraints)**: Utilizes a distributed lock in `Redis` to prevent "thundering herd" race conditions. Subsequent retries with the same `idempotency_key` are served directly from the cache, completely bypassing the database and the downstream microservices. A DB-level `UNIQUE` constraint on `idempotency_key` provides a final safety net for any concurrent duplicate that slips past the Redis lock.
  - **Egress Safety (SQS)**: Operations execute asynchronously downstream via SQS queues containing rigid payload correlation IDs. Downstream workers can infinitely replay dropped SQS events without mutating side-effects.

### 3. Risk Engine Service (`risk-engine-service`)
The operational orchestrator of business intelligence.
- **Rules-First Heuristic Engine**: Checks incoming transactions against a modular pipeline of Python-based hard heuristics (e.g. `AccountAgeRule`, `VelocityRule`). It guarantees absolute, deterministic compliance limits are honored natively.
- **Account Profile Cache**: Behavioural profiles (velocity history, known devices/receivers, risk flags) are cached in Redis with a 30s TTL. Repeat senders skip the Postgres round-trip entirely on the synchronous scoring path. The cache is invalidated by the SQS worker after each profile upsert, so analytics always settle on fresh data within one processing cycle.
- **ML Aggregation (The Scorer)**: Dynamically weights rule-based intelligence against purely statistical ML intelligence. Algorithmically suppresses false-positive noise for new accounts and low-value transactions where the ML model has insufficient signal.
- **Asynchronous Post-Processing**: The Risk Engine returns its verdict immediately after scoring. Writing the full `RiskResult` to the database, dispatching webhooks, and triggering the Analyst Service are all offloaded to a background SQS Worker — they never appear on the response wall-clock time.

### 4. ML Service (`ml-service`)
Sub-millisecond machine learning inference isolation module.
- **ONNX Predictor**: Wraps a heavily imbalanced, high-depth XGBoost model into `ONNX Runtime` for sub-millisecond inference. Measured at **0.4–0.8ms** per prediction with a total gRPC round-trip of ~1.7ms over the Docker bridge network. Uses a 20-feature behavioural vector including velocity, device novelty, amount ratios, and account age.
- **Zero-Downtime Hot-Swapping**: Features a thread-safe singleton lock coupled to a `Boto3 S3Client`. It exposes a `ReloadModel` gRPC RPC that pulls `risk_model.onnx` from AWS S3 directly into memory, hot-swapping the inference model *without dropping a single TCP connection* or requiring a container restart.

### 5. Analyst Service (`analyst-service`)
The investigation and MLOps orchestration hub. It isolates heavy LLM inference from the low-latency Risk Engine.
- **AI Fraud Investigation**: When a transaction is flagged for `REVIEW` or `BLOCK`, the Risk Engine publishes an SQS message. The Analyst Service consumes this message and triggers a **LlamaIndex ReAct Agent** to reason about the risk factors, generating a human-readable investigation report. The LLM provider is fully configurable — Ollama, Anthropic, OpenAI, or Gemini — via `LLM_PROVIDER` and `LLM_MODEL` in `.env`.
- **Self-Healing MLOps**: Implements a deterministic **LlamaIndex Workflow** that monitors model performance (e.g., false-positive rates). If the LLM determines that Concept or Data Drift has occurred, it automatically triggers a retraining pipeline and calls the ML Service's hot-swap endpoint.

---

## 🎯 Guided Test Personas

To save you from manually generating dozens of transactions to "warm up" the ML models, the databases have been pre-seeded with 6 months of historical data mapped to specific personas.

### Persona 1: The Loyal Customer (B2B Client 1)
- **Tenant ID:** `56f292e4-80f1-704a-38f4-42f883cf5d91`
- **Background:** An established account with 6 months of history, consistently making high-value transactions (£500 - £2,500) using a trusted device and known receivers.
- **Expected Outcome:** Fast `APPROVE` with a low risk score, demonstrating that the ML model understands user baseline behavior and doesn't blindly block high amounts.

**Test Payload (`POST /transactions`):**
```json
{
  "amount": 2450.00,
  "currency": "GBP",
  "sender_id": "good_user_01",
  "receiver_id": "merchant_trusted",
  "sender_country": "GB",
  "receiver_country": "GB",
  "device_fingerprint": "device_good_1",
  "ip_address": "192.168.1.5",
  "idempotency_key": "test_good_high_01",
  "channel": "web",
  "transaction_type": "PAYMENT"
}
```

### Persona 2: The Erratic Fraudster (B2B Client 2)
- **Tenant ID:** `5692b244-30d1-7072-584e-1b3637f04ab7`
- **Background:** Brand new account that has made 15+ massive transactions spanning Russia, Nigeria, and the US in the last 48 hours using untrusted devices.
- **Expected Outcome:** Triggers the ML anomaly detection and velocity rules, resulting in a `REVIEW` or `BLOCK`. This instantly queues an automated Agentic AI Deep-Dive.

**Test Payload (`POST /transactions`):**
```json
{
  "amount": 4800.00,
  "currency": "GBP",
  "sender_id": "good_user_01",
  "receiver_id": "shady_crypto_wallet",
  "sender_country": "GB",
  "receiver_country": "RU",
  "device_fingerprint": "device_new_untrusted",
  "ip_address": "103.45.2.19",
  "idempotency_key": "test_bad_spike_01",
  "channel": "mobile_app",
  "transaction_type": "TRANSFER"
}
```

---

## 🧠 Architectural Decisions: The "Why"

**Why gRPC instead of REST internally?**
REST relies on HTTP/1.1 and JSON parsing, which introduces unacceptable latency overhead for a synchronous fraud evaluation pipeline. By utilizing gRPC, Aegis Risk benefits from HTTP/2 multiplexing and strongly typed Protobuf serialization, allowing the Risk Engine to query the ML Service in under 1ms.

**Why decouple the Analyst Service from the Risk Engine?**
The Risk Engine must return a deterministic `APPROVE/REVIEW/BLOCK` verdict in milliseconds. LLMs (used for generating human-readable fraud reports) can take seconds to stream a response. By moving the LLM investigation to the `analyst-service` and triggering it asynchronously via SQS, the critical path remains blazing fast while analysts still receive deep-dive reports.

**Why use Redis AND Database Constraints for Idempotency?**
Database Unique Constraints are the ultimate source of truth but are expensive to hit under load. To protect the database and handle high-concurrency race conditions, the `transaction-service` implements a **Double-Checked Locking** pattern using Redis:
1. **Initial Cache Hit**: Instantly returns a cached response for known keys.
2. **Atomic Distributed Lock**: Uses Redis `SET key value NX` to ensure only one worker can process a specific `idempotency_key` at a time.
3. **Double-Check**: Re-verifies the cache after acquiring the lock to ensure a concurrent request didn't finish during the acquisition window.
This multi-layered approach solves the "thundering herd" problem and guarantees that even under extreme load, a transaction is never processed twice.

**Why use ONNX for ML Inference?**
Python-based ML frameworks (like Scikit-Learn or XGBoost native predictors) carry significant overhead and struggle with Python's Global Interpreter Lock (GIL) during concurrent requests. Compiling the model to ONNX allows the `ml-service` to execute the computational graph directly in C++, utilizing thread pools effectively. Measured inference time is **0.4–0.8ms**, with a full gRPC round-trip of ~1.7ms — meaning ML scoring contributes less than 2% of the total request wall-clock time.

**How do we ensure tasks aren't lost if a service crashes?**
Aegis Risk implements a **Reliable Consumer (acks_late)** pattern using SQS. Instead of deleting a message immediately upon receipt, the workers (Risk Engine and Analyst Service) only invoke `delete_message` *after* the entire processing pipeline—database writes, external calls, and event publishing—is successfully completed. If a container crashes mid-task, the SQS visibility timeout expires, and the message is automatically returned to the queue for another worker to pick up, guaranteeing **at-least-once delivery** and zero data loss.

---

## 💰 Efficiency & Operations

**AI Cost Optimization**
The `analyst-service` uses expensive LLM tokens sparingly. The system only triggers an AI investigation when the Risk Engine returns a `BLOCK` or `REVIEW` decision. `APPROVE` decisions skip the LLM entirely, drastically reducing compute costs while focusing human-analyst-ready intelligence only on suspicious behavior.

**Manual Re-Investigation**
The API Gateway exposes a `POST /transactions/{transaction_id}/reinvestigate` endpoint. This allows human analysts or automated triggers to manually re-queue a transaction for the `analyst-service`. This is critical for operational resilience, allowing for re-tries if the original AI inference failed or if a fresh report is needed after new data becomes available.
