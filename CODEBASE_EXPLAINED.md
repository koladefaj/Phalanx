# AegisRisk — Complete Codebase Explanation

> Use this as your interview reference. Every section maps to a question category an interviewer would ask.

---

## 1. What Is This System?

**AegisRisk** is a production-grade, real-time fraud detection platform for financial transactions. It is built as a microservices architecture that combines deterministic rule-based scoring with ML inference and AI-powered investigation.

**Core value proposition**: Return a fraud decision (APPROVE / REVIEW / BLOCK) in under 300ms for any incoming transaction, while running deeper AI investigation asynchronously in the background.

**Who uses it**: B2B fintech clients (payment processors, banks) that need a managed fraud detection API. Each client is isolated by tenant ID derived from their Cognito JWT.

---

## 2. High-Level Architecture

```
External Client
      │
      │ REST (HTTP/1.1 + JWT)
      ▼
 ┌─────────────────┐
 │   API Gateway   │  ← JWT validation, rate limiting, routing
 └────────┬────────┘
          │ gRPC
          ▼
 ┌──────────────────────┐
 │  Transaction Service │  ← Idempotency, ledger, SQS publish
 └──────────┬───────────┘
            │ gRPC (sync, <300ms)
            ▼
 ┌───────────────────────┐
 │   Risk Engine Service │  ← Rules + ML ensemble scoring
 └────┬──────────────────┘
      │ gRPC (sync)          │ SQS (async)
      ▼                      ▼
 ┌────────────┐     ┌────────────────────┐
 │ ML Service │     │  Risk Engine Worker│  ← Updates DB, triggers analyst
 └────────────┘     └────────┬───────────┘
                             │ SQS (async)
                             ▼
                   ┌──────────────────────┐
                   │   Analyst Service    │  ← LLM investigation
                   └──────────────────────┘
```

**Communication patterns**:
- **REST**: API Gateway ↔ external clients
- **gRPC (HTTP/2 + Protobuf)**: all internal service-to-service calls
- **AWS SQS**: async event queues for post-processing
- **Redis**: idempotency cache, velocity counters, burst detection
- **PostgreSQL**: persistent state (transactions, risk results, account profiles)

**Why gRPC internally?** HTTP/2 multiplexing + Protobuf binary serialization eliminates JSON parsing overhead and HTTP/1.1 connection limits. This is critical for the synchronous <300ms scoring path.

---

## 3. Service-by-Service Breakdown

### A. API Gateway (`services/api-gateway`)

**Role**: The only internet-facing service. Validates JWTs, enforces rate limits, and forwards requests downstream via gRPC.

**Key files**:
- `app/main.py` — FastAPI app with lifespan management, opens gRPC channel to transaction-service on startup
- `app/routers/transactions.py` — `POST /transactions`, `GET /transactions/{id}`, `POST /transactions/{id}/reinvestigate`
- `app/routers/auth.py` — OAuth2 flow redirecting to AWS Cognito
- `app/routers/mlops.py` — `POST /mlops/reload-model` (admin only)
- `app/middleware/auth/cognito.py` — RS256 JWT validation against Cognito JWKS endpoint, extracts `custom:tenant_id`
- `app/middleware/rate_limit.py` — Redis-backed sliding window rate limiter (100 req / 60s per client)
- `app/grpc/clients/transaction_client.py` — Wraps gRPC stub, maps Protobuf responses to Pydantic schemas

**Critical patterns**:
- Correlation ID is generated here and injected into all downstream gRPC metadata
- Rate limiter uses Redis `SADD` + `EXPIRE` — no Lua scripts, just atomic set operations
- gRPC channel health-checked before the API accepts any traffic (lifespan hook)
- JWT validation is fail-secure: if Cognito JWKS is unreachable, request is rejected

---

### B. Transaction Service (`services/transaction-service`)

**Role**: Authoritative transaction ledger. Guarantees exactly-once processing via idempotency, orchestrates synchronous risk scoring, and emits events for async work.

**Key files**:
- `app/main.py` — gRPC server on port 50051
- `app/services/transaction_service.py` — Core flow:
  1. Validate idempotency (Redis lock → cache check → DB unique constraint)
  2. Pre-generate `transaction_id = uuid4()` before touching the DB
  3. DB SELECT only — check idempotency, return early on duplicate
  4. Call Risk Engine synchronously via gRPC with the pre-generated UUID
  5. Single DB INSERT with the final status (`APPROVED` / `REVIEW` / `BLOCKED`) — no intermediate `RECEIVED` row, no UPDATE step
  6. `IntegrityError` handler covers concurrent duplicates that slip past the Redis lock
  7. Publish SQS event for async post-processing
  8. Return `RiskAssessment` to API Gateway
- `app/services/idempotency_service.py` — Double-checked locking (see Section 6A)
- `app/models/transaction.py` — SQLAlchemy ORM with JSONB metadata column
- `app/repo/transaction_repo.py` — DB access layer with composite indexes
- `app/queue/sqs_publisher.py` — Async SQS publish via aioboto3

**Database schema** (`aegis_transactions` database):
```sql
transactions (
  transaction_id    UUID PRIMARY KEY,
  idempotency_key   VARCHAR(128),
  client_id         VARCHAR(128),          -- multi-tenant isolation
  amount            NUMERIC(10,2),
  sender_id         VARCHAR(128),
  receiver_id       VARCHAR(128),
  sender_country    VARCHAR(2),
  receiver_country  VARCHAR(2),
  device_fingerprint VARCHAR(256),
  ip_address        INET,
  channel           VARCHAR(32),
  status            VARCHAR(32),
  created_at        TIMESTAMPTZ,
  updated_at        TIMESTAMPTZ,
  UNIQUE(idempotency_key, client_id)        -- DB-level safety net
)
-- Indexes: (sender_id, status), created_at
```

**Failure behaviour**: If the Risk Engine call fails, the transaction defaults to `REVIEW` — never silently approved.

---

### C. Risk Engine Service (`services/risk-engine-service`)

**Role**: The brain. Orchestrates rule evaluation + ML scoring, returns a deterministic fraud decision. Also runs an async SQS worker for post-processing.

**Key files**:
- `app/engine/orchestrator.py` — Synchronous scoring pipeline (described in Section 6B)
- `app/engine/scorer.py` — Score calculation and thresholding
- `app/engine/rules/` — 8 individual rule implementations
- `app/worker.py` — Async SQS consumer (acks-late pattern)
- `app/models/account_profile.py` — Behavioral profile per sender

**The 8 Rules**:

| Rule | Trigger Condition | Score |
|------|-------------------|-------|
| `HighValueRule` | Amount > $10,000 | 1.0 |
| `VelocitySpikeRule` | > 3 transactions/hour | Proportional to overage |
| `GeoMismatchRule` | Sender country ≠ Receiver country | 0.3 |
| `DeviceFingerprintRule` | Device not seen before for this sender | 0.5 |
| `UnusualHourRule` | Transaction between 12 AM – 5 AM | 0.3 |
| `AccountAgeRule` | Account < 30 days old + amount > $500 | 0.3–1.0 (grace period < $250 → 0.1) |
| `FailedBurstRule` | > 5 blocked transactions in 30 minutes | 0.8 |
| `NewReceiverRule` | First time sending to this receiver | 0.4 |

**Account Profile schema** (`aegis_risk` database):
```sql
account_profiles (
  account_id              VARCHAR(64) PRIMARY KEY,
  total_txn_count         BIGINT,
  total_volume_lifetime   NUMERIC(20,2),
  txn_count_1h            INTEGER,
  txn_count_24h           INTEGER,
  txn_count_30d           INTEGER,
  total_volume_1h         NUMERIC(20,2),
  total_volume_24h        NUMERIC(20,2),
  total_volume_30d        NUMERIC(20,2),
  avg_txn_amount          NUMERIC(10,2),
  max_txn_amount          NUMERIC(10,2),
  fraud_txn_count         INTEGER,
  blocked_txn_count       INTEGER,
  is_high_risk            BOOLEAN,
  known_receiver_ids      VARCHAR[],
  known_device_fingerprints VARCHAR[],
  first_seen_at           TIMESTAMPTZ,
  last_seen_at            TIMESTAMPTZ,
  window_reset_at_1h      TIMESTAMPTZ,
  version                 INTEGER          -- optimistic locking
)
```

**Redis keys used by Risk Engine**:
| Key Pattern | Type | TTL | Purpose |
|-------------|------|-----|---------|
| `profile:{sender_id}` | JSON string (SETEX) | 30s | Account profile cache — skips DB on cache hit |
| `velocity:1h:{sender_id}` | Counter (INCR) | 1h | Real-time transaction count |
| `failed:1h:{sender_id}` | Counter (INCR) | 1h | Blocked transaction count |
| `burst:device:{sender_id}` | Set (SADD) | 5min | New devices in burst window |
| `burst:receiver:{sender_id}` | Set (SADD) | 5min | New receivers in burst window |

`profile:{sender_id}` is cached via `_load_profile_cached()` in the orchestrator. The SQS worker calls `DEL profile:{sender_id}` after each `upsert_after_transaction` so stale data settles within one processing cycle (typically 1–3s). Redis is used for velocity counters because it's more accurate (updated synchronously before the DB write) and avoids row-level locking on hot accounts.

**SQS Worker (acks-late pattern)**:
1. Poll `aegis-transactions` SQS queue
2. Update `account_profiles` (upsert) with new transaction data
3. Persist full `RiskResult` to DB
4. If decision is BLOCK or REVIEW → publish to `aegis-agent-investigations` queue
5. Publish `RiskCompleted` event (for webhooks)
6. **Only then** delete the SQS message

Step 6 is the key: if the worker crashes between steps 2–5, the message reappears after the visibility timeout and is reprocessed. No data is lost.

---

### D. ML Service (`services/ml-service`)

**Role**: Sub-millisecond fraud probability scoring via ONNX XGBoost inference.

**Key files**:
- `app/core/predictor.py` — Singleton ONNX inference session with thread-safe hot-swap
- `app/core/s3_client.py` — Fetches model artifacts from S3
- `app/scripts/trainer.py` — Offline training script (outputs `.onnx` + `metadata.json`)

**Why ONNX over native XGBoost?**
- XGBoost's Python API carries ~2–5ms overhead per prediction (Python interpreter + GIL)
- ONNX Runtime executes in C++ — completely bypasses the Python GIL
- Achieves sub-millisecond inference
- Model is portable and versionable as a single binary artifact

**20 input features** (built in `AccountProfile.to_feature_dict()`):
```
# Transaction context
amount_vs_avg_ratio        # current amount ÷ sender average (capped at 50×)

# Lifetime account stats
sender_txn_count           # total transactions ever
sender_total_volume        # lifetime spend
sender_avg_amount          # running average (Welford online algorithm)
sender_max_amount          # largest single transaction

# Account age & novelty signals
account_age_hours          # hours since first transaction
is_new_account             # account < 24h old (bool)
is_new_receiver            # first time sending to this receiver (bool)
is_new_device              # unrecognised device fingerprint (bool)
is_dormant                 # no activity in last 30 days (bool)

# Network diversity
unique_receiver_count      # number of distinct receivers
unique_device_count        # number of distinct device fingerprints

# Risk history
fraud_txn_count            # confirmed fraud transactions
blocked_txn_count          # transactions blocked by rules

# Velocity windows
txn_count_1h               # transactions in last hour
txn_count_24h              # transactions in last 24 hours
total_volume_1h            # spend in last hour
total_volume_24h           # spend in last 24 hours
velocity_score             # normalised txn_count_1h ÷ MAX_TXN_PER_HOUR
fraud_rate                 # fraud_txn_count ÷ total_txn_count × 100
```

**Hot-swap mechanism** (zero-downtime model update):
1. Admin calls `POST /mlops/reload-model`
2. API Gateway → Risk Engine → ML Service `ReloadModel` RPC
3. Predictor acquires a `threading.Lock`
4. Atomically replaces: ONNX session, input name, feature names, threshold, version
5. No in-flight requests interrupted, no TCP connections dropped
6. All subsequent calls use the new model

**gRPC interface**:
```protobuf
rpc ScoreTransaction(ScoreTransactionRequest) returns (ScoreTransactionResponse)
rpc ReloadModel(ReloadModelRequest) returns (ReloadModelResponse)
```

---

### E. Analyst Service (`services/analyst-service`)

**Role**: AI-powered fraud investigation for flagged transactions. Also houses the MLOps worker that monitors for model drift and triggers retraining.

**Key files**:
- `app/services/llama_agent.py` — two-phase flow: ReActAgent reasoning → structured extraction
- `app/core/llm.py` — LlamaIndex LLM factory (agent reasoning loop)
- `app/core/structured_llm.py` — **instructor-based extraction factory** (final structured output)
- `app/schemas/investigation.py` — `FraudInvestigationReport` Pydantic model
- `app/queue/sqs_consumer.py` — `AnalystInvestigationWorker`: polls `aegis-agent-investigations`
- `app/queue/mlops_consumer.py` — `MLOpsWorker`: monitors model performance, triggers retraining
- `app/tools/agent_tools.py` — 4 tools the LLM can call

**Agent tools**:
1. `get_sender_profile()` — Lifetime behavior stats, fraud rate, risk flags
2. `fetch_recent_transaction_patterns()` — Last 10 transactions (IP, device, country, timing)
3. `inspect_automated_decision()` — Which rules fired, ML anomaly score, confidence
4. `check_external_ip_intelligence()` — Third-party IP geolocation + VPN detection

**Two-phase investigation**: The original approach used regex to parse LLM text, which breaks silently when a model changes its output format. The current approach separates reasoning from extraction:

```
Phase 1 — ReActAgent (LlamaIndex)
  Thought → Action (tool call) → Observation → ... → final narrative text
                    ↓
Phase 2 — Structured extraction (instructor)
  One focused LLM call converts the narrative into a validated Pydantic model.
  instructor retries automatically if the response fails schema validation.
                    ↓
  FraudInvestigationReport (validated, typed, no regex)
```

**`FraudInvestigationReport`** (`app/schemas/investigation.py`):
```python
class FraudInvestigationReport(BaseModel):
    summary: str                                           # 2-3 sentence narrative
    risk_factors: list[str]                                # one item per signal
    verdict: Literal["FRAUDULENT", "SUSPICIOUS", "LEGITIMATE"]
    recommendation: Literal["BLOCK", "REVIEW", "ALLOW"]
    confidence: float                                      # 0.0 – 1.0
```
`servicer.py` and `sqs_consumer.py` access `report.verdict`, `report.confidence`, `report.summary`, etc. directly — no parsing, no fallbacks.

**Cost optimization**: The analyst is only triggered for BLOCK and REVIEW decisions — APPROVE transactions skip the LLM entirely. This keeps operational costs proportional to actual risk.

**LLM provider factories** (`app/core/llm.py` + `app/core/structured_llm.py`):
The service uses two factories that both read `LLM_PROVIDER` + `LLM_MODEL` from `.env`:

| `LLM_PROVIDER` | Agent loop (LlamaIndex) | Extraction (instructor) | Mechanism |
|----------------|-------------------------|-------------------------|-----------|
| `ollama` | `llama-index-llms-ollama` | instructor + OpenAI-compat `/v1` | `Mode.JSON` |
| `anthropic` | `llama-index-llms-anthropic` | instructor + `AsyncAnthropic` | tool_use (native) |
| `openai` | `llama-index-llms-openai` | instructor + `AsyncOpenAI` | `json_schema` response format |
| `gemini` | `llama-index-llms-gemini` | instructor + `GenerativeModel` (sync → `to_thread`) | `GEMINI_JSON` |

Both factories validate the required API key at startup. Misconfiguration is caught at deploy time, not mid-investigation.

**MLOps worker**:
- Monitors false positive rates and data drift signals
- If drift detected → triggers retraining pipeline
- Calls ML Service's `ReloadModel` RPC to hot-swap the new model

---

### F. Notification Service (`services/notification-service`)

**Role**: Webhook delivery with HMAC signing and retry logic. Consumes the `aegis-risk-completed` SQS queue and fans out to all webhooks registered by the transaction's tenant.

**Key files**:
- `app/main.py` — gRPC server (port 50055) + SQS worker, concurrent with `asyncio.gather`
- `app/grpc/server/servicer.py` — implements 4 RPCs: `RegisterWebhook`, `SendNotification`, `GetWebhookStatus`, `HealthCheck`
- `app/queue/sqs_consumer.py` — `NotificationWorker`: polls `aegis-risk-completed`, looks up active webhooks for the tenant, delivers, acks-late
- `app/services/webhook_delivery.py` — HTTP delivery via httpx, HMAC-SHA256 request signing, up to `WEBHOOK_MAX_RETRIES` attempts per URL
- `app/repositories/webhook_repo.py` — CRUD on `webhooks` table: create, lookup by `(client_id, event)`, increment delivery/failure counters
- `app/models/webhook.py` — SQLAlchemy `webhooks` table
- `alembic/` — migration that creates the `webhooks` table with indexes on `client_id` and `(client_id, is_active)`

**Database schema** (`aegis_notifications` database):
```sql
webhooks (
  webhook_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id        VARCHAR(128) NOT NULL,   -- tenant isolation
  url              VARCHAR(512) NOT NULL,
  events           VARCHAR[],               -- e.g. ['risk.completed']
  is_active        BOOLEAN      DEFAULT true,
  delivery_count   INTEGER      DEFAULT 0,
  failure_count    INTEGER      DEFAULT 0,
  created_at       TIMESTAMPTZ  DEFAULT now(),
  last_delivery_at TIMESTAMPTZ
  -- Indexes: client_id, (client_id, is_active)
)
```

**HMAC signing**: Every outgoing request includes `X-Aegis-Signature: sha256=<hex>` and `X-Aegis-Timestamp` headers computed from `WEBHOOK_SECRET`. The receiving client verifies the signature to confirm authenticity.

**SQS flow**: The `aegis-risk-completed` message carries `client_id` (propagated from transaction-service → risk worker → completion event). The notification worker reads it, queries all active webhooks for that tenant subscribing to `risk.completed`, and delivers to each. Acks the SQS message only after all delivery attempts complete (acks-late).

**gRPC interface**:
```protobuf
rpc RegisterWebhook(RegisterWebhookRequest)   returns (RegisterWebhookResponse)
rpc SendNotification(SendNotificationRequest) returns (SendNotificationResponse)
rpc GetWebhookStatus(GetWebhookStatusRequest) returns (GetWebhookStatusResponse)
rpc HealthCheck(HealthCheckRequest)           returns (HealthCheckResponse)
```

---

## 4. Authentication & Authorization

**Technology**: AWS Cognito with asymmetric RS256 JWTs.

**Login flow**:
1. Client calls `GET /auth/login` → redirected to Cognito hosted UI
2. Cognito validates credentials → returns ID token
3. ID token contains:
   - `sub`: user ID
   - `email`: user email
   - `custom:tenant_id`: B2B client identifier (set by a Post-Confirmation Lambda)
   - `cognito:groups`: role assignment
4. Client includes JWT as `Authorization: Bearer <token>` on all requests
5. API Gateway middleware validates JWT signature using Cognito's public JWKS endpoint
6. `custom:tenant_id` is extracted and passed to all downstream services as `client_id`

**RBAC groups** (assigned automatically by Cognito Lambda trigger):

| Group | Condition | Permissions |
|-------|-----------|-------------|
| `admin` | `@aegisrisk.internal` email | All endpoints including model reload |
| `analyst` | `@analyst.aegisrisk.internal` email | Transactions + reinvestigate |
| `client` | Everyone else | Submit transactions only |

**Multi-tenancy**: Every DB query is filtered by `client_id`. A client cannot see another tenant's transactions even if they have a valid JWT.

---

## 5. Idempotency — Double-Checked Locking

**Problem**: Under high concurrency, multiple retries of the same transaction can hit the service simultaneously (thundering herd). A naive DB unique constraint check causes expensive serialized DB writes.

**Solution** (Redis + DB layered):

```
Request arrives with idempotency_key
        │
        ▼
1. Redis GET idempotency:{key}
   Hit? → return cached response immediately (sub-ms)
        │ Miss
        ▼
2. Redis SET idempotency:lock:{key} NX EX 60
   Fail? → another thread has the lock → wait / return 409
        │ Acquired
        ▼
3. Redis GET idempotency:{key}  ← double-check after acquiring lock
   Hit? → return cached response (another thread finished while we waited)
        │ Miss
        ▼
4. Process transaction (risk scoring, DB write)
        │
        ▼
5. Redis SETEX idempotency:{key} 86400 <response>
        │
        ▼
6. Return response. Lock expires automatically after 60s.
```

**Why double-check at step 3?** Between step 1 (miss) and step 2 (lock acquired), another thread could have completed the work. Without the double-check, you'd do the work twice.

**DB unique constraint** on `(idempotency_key, client_id)` is the final safety net — Redis is a performance optimization, not the source of truth.

---

## 6. Risk Scoring Pipeline

### Synchronous path (must complete < 300ms)

```
Transaction arrives at Risk Engine
        │
        ▼
1. Load account_profile (_load_profile_cached):
   - Redis GET profile:{sender_id}  → hit: deserialise JSON, skip DB
   - Miss: DB get_or_create         → cache result with 30s SETEX
        │
        ▼
2. Enrich with real-time Redis counters (all 4 ops run concurrently via asyncio.gather):
   - SADD burst:device:{sender_id} {device_fingerprint}
   - SADD burst:receiver:{sender_id} {receiver_id}
   - INCR velocity:1h:{sender_id}
   - GET failed:1h:{sender_id}
   TTL refreshes (EXPIRE) are create_task fire-and-forget — off the hot path
        │
        ▼
3. Evaluate all 8 rules (stateless, can run in parallel)
   Each rule → { triggered: bool, score: float, reason: str }
        │
        ▼
4. Aggregate rule score:
   - Weighted sum: HIGH severity × 2.5, MEDIUM × 1.2, LOW × 0.7
   - Multiple HIGH rules → 1.2× boost
   - Normalize to 0–100
        │
        ▼
5. Call ML Service (ScoreTransaction gRPC)
   - On failure → fallback score = 0.0 (rules-only decision)
   - New account (< 24h) + small amount (< $250) → dampen ML by ÷10
   - ML score < 0.90 → use score × 0.1 (suppress noise)
        │
        ▼
6. Final score = (rule_score × 0.70) + (ml_score × 100 × 0.30)
        │
        ▼
7. Categorize:
   0–40  → LOW risk    → APPROVE
   40–60 → MEDIUM risk → REVIEW
   60–80 → HIGH risk   → BLOCK
   80+   → CRITICAL    → BLOCK
        │
        ▼
8. Return RiskAssessment to Transaction Service
```

**Why rules-first with 70% weight?** Rules are deterministic, auditable, and comply with regulatory requirements. ML models can drift or produce false positives on new account types. Rules act as a hard governor — the ML signal refines, it does not override.

**ML dampening rationale**: A model trained on historical fraud data will overfit to certain patterns (e.g., new accounts = suspicious) even when the transaction is legitimate onboarding. Dampening prevents false positives during normal customer acquisition.

---

## 7. Async Post-Processing (SQS Workers)

After the synchronous response is returned, two workers handle deferred work:

### Risk Engine Worker
Triggered by: `aegis-transactions` SQS queue

1. Upsert `account_profiles` with the new transaction data
2. `DEL profile:{sender_id}` — invalidate Redis cache so the next evaluation sees fresh DB state
3. Persist `RiskResult` to DB (full record including rule flags, ML score, `ml_fallback_used`)
4. If BLOCK or REVIEW → publish to `aegis-agent-investigations`
5. Publish `RiskCompleted` event (triggers webhook delivery)
6. Delete SQS message

### Analyst Worker
Triggered by: `aegis-agent-investigations` SQS queue

1. Fetch transaction and risk result from DB
2. Run LlamaIndex ReAct agent (typically 5–15 seconds)
3. Extract `FraudInvestigationReport` via instructor (validated Pydantic model)
4. Write `analyst_summary` + `agent_risk_factors` to `risk_results` table
5. Delete SQS message

**Acks-late pattern**: The SQS message is only deleted after all work is persisted. If the worker process crashes mid-execution, the message reappears after the visibility timeout (30s for risk worker, 180s for analyst) and another worker picks it up. This guarantees at-least-once processing.

---

## 8. Infrastructure & Deployment

### Docker Compose services

| Service | Port | Technology |
|---------|------|------------|
| `postgres` | 5432 | PostgreSQL 16 |
| `redis` | 6379 | Redis 7 |
| `localstack` | 4566 | LocalStack (mocks SQS + Cognito for dev) |
| `api-gateway` | 8000 | FastAPI |
| `transaction-service` | 50051 | Python gRPC |
| `risk-engine-service` | 50052 | Python gRPC |
| `ml-service` | 50053 | Python gRPC |
| `analyst-service` | 50056 | Python gRPC + pluggable LLM (Ollama / Anthropic / OpenAI / Gemini) |
| `notification-service` | 50055 | Python gRPC + SQS worker |

**Three separate databases** in one Postgres instance (created by `infra/init-databases.sql`):
- `aegis_transactions` — owned by transaction-service
- `aegis_risk` — owned by risk-engine-service
- `aegis_notifications` — owned by notification-service

Each service only has credentials for its own database. This enforces data ownership boundaries even within a monolithic Postgres deployment.

**LocalStack** mocks AWS SQS and Cognito locally. `infra/localstack-init.sh` creates the SQS queues on container startup:
- `aegis-transactions`
- `aegis-agent-investigations`
- `aegis-risk-completed`

**Health checks**: Every service has a health check defined in `docker-compose.yml`. Dependent services use `condition: service_healthy` so they don't start until their dependencies are ready.

### Running the stack
```bash
make proto                                           # compile .proto → Python stubs
docker-compose up -d --build                        # start all services
python generate_seed_data.py                        # generate test data
cat seed_data.sql | docker exec -i postgres psql -U aegis  # load seed data
```

---

## 9. Shared Library (`shared/aegis_shared`)

All services import from this package to avoid code duplication:

| Module | Contents |
|--------|----------|
| `enums.py` | `TransactionStatus`, `RiskLevel`, `RiskDecision`, `RuleFlag` |
| `schemas/transaction.py` | `TransactionCreate`, `TransactionResponse` Pydantic models |
| `schemas/risk.py` | `RiskAssessment`, `RiskFactor`, `RiskResult` |
| `schemas/auth.py` | `AuthUser`, JWT claims |
| `schemas/webhook.py` | Webhook registration/notification models |
| `utils/logging.py` | Structured JSON logging with correlation ID |
| `utils/tracing.py` | Correlation ID context (thread-local storage) |
| `utils/sqs.py` | Async aioboto3 session management |
| `utils/redis.py` | Async Redis connection pool |
| `grpc/interceptors/logging_server.py` | Server-side gRPC logging interceptor |
| `grpc/interceptors/correlation_client.py` | Client-side correlation ID injection into gRPC metadata |
| `generated/*.py` | Compiled Protobuf stubs (source of truth: `proto/` directory) |

**Protobuf files** (`proto/`):
- `transaction.proto` — `SubmitTransaction`, `GetTransaction` RPCs
- `risk_engine.proto` — `EvaluateRisk` RPC
- `ml_service.proto` — `ScoreTransaction`, `ReloadModel` RPCs
- `analyst_service.proto` — `InvestigateTransaction` RPC
- `notification.proto` — `RegisterWebhook`, `SendNotification` RPCs
- `common.proto` — shared message types (correlation ID wrapper, etc.)

---

## 10. Configuration Management

All services use `pydantic_settings.BaseSettings` to load config from environment variables (`.env` file in development, injected secrets in production).

**Key configuration values**:

| Variable | Default | Purpose |
|----------|---------|---------|
| `RULE_SCORE_WEIGHT` | 0.70 | Weight of rule score in final ensemble |
| `ML_SCORE_WEIGHT` | 0.30 | Weight of ML score in final ensemble |
| `VELOCITY_MAX_TRANSACTIONS` | 3 | Threshold before velocity rule fires |
| `VELOCITY_WINDOW_MINUTES` | 60 | Rolling window for velocity |
| `ACCOUNT_AGE_RISK_DAYS` | 30 | Account younger than this is flagged |
| `FAILED_BURST_THRESHOLD` | 5 | Blocked txns before burst rule fires |
| `FAILED_BURST_WINDOW_MINUTES` | 30 | Rolling window for burst detection |
| `WORKER_POLL_INTERVAL` | 5s | How often workers poll SQS |
| `WORKER_VISIBILITY_TIMEOUT` | 30s (risk) / 180s (analyst) | SQS message lock duration |
| `WORKER_MAX_MESSAGES` | 10 | Batch size per SQS poll |

---

## 11. Resilience & Fault Tolerance

| Failure | Behaviour |
|---------|-----------|
| Redis unavailable | Fall back to rules-only scoring; idempotency falls back to DB unique constraint |
| ML Service down | Risk Engine uses fallback score 0.0; rules make the final decision |
| Analyst Service down | Worker skips investigation trigger; transaction still processed |
| SQS unavailable | Transaction response is still returned; async work queued for retry |
| Cognito JWKS unreachable | Fail-secure: all requests rejected (no JWT validation = no access) |
| Worker crash mid-processing | SQS visibility timeout expires; message redelivered to next worker |
| DB write fails | Transaction marked REVIEW (never silently approved) |

---

## 12. Key Design Decisions & Tradeoffs

| Decision | Why | Tradeoff |
|----------|-----|----------|
| gRPC internally, REST externally | Sub-ms latency on critical path; type-safe contracts | Proto compilation step, steeper learning curve |
| Async post-processing via SQS | Keep critical path under 300ms; decouple LLM from request path | Eventual consistency on account profiles and analyst reports |
| Rules-first with 70/30 weighting | Deterministic compliance floor; prevents ML false positives | Underutilizes ML signal in edge cases |
| ONNX over native XGBoost | Bypasses Python GIL; sub-ms inference | Model must be exported offline; harder to debug |
| Redis velocity counters | Faster and more accurate than DB aggregations under load | Extra cache layer; counters can drift if Redis restarts |
| Double-checked locking idempotency | Prevents thundering herd on DB from retry storms | Extra Redis round-trip on cache miss |
| Acks-late SQS pattern | Zero data loss if worker crashes | Requires idempotent processing (duplicate messages possible) |
| Three separate databases | Enforce service data ownership boundaries | More complex connection management |
| LLM investigation async only | Cost optimization — APPROVE skips LLM entirely | Analysts see delayed reports for REVIEW cases |
| LLM-agnostic provider factory | Swap Ollama → Claude → GPT with two `.env` changes, no code edits | All providers must be LlamaIndex-compatible; Gemini constructor differs slightly (`model_name` vs `model`) |
| instructor for structured extraction | Replaces fragile regex parsing with Pydantic-validated models; retries automatically on bad output | Two LLM calls per investigation (agent loop + extraction); Gemini SDK is sync so extraction runs in a thread pool |
| Cognito `custom:tenant_id` | Multi-tenancy without custom identity infrastructure | Coupled to AWS; Cognito Lambda trigger must be configured |
| ML dampening for new accounts | Prevents false positives during customer onboarding | May miss real fraud on brand-new compromised accounts |
| `client_id` propagated through SQS chain | Notification service needs tenant ID to route webhooks correctly | Must be included at every hop: transaction → risk worker → completion event |

---

## 13. Interview Question Cheat Sheet

**"Walk me through what happens when a transaction is submitted."**
> REST POST hits API Gateway → JWT validated, rate limit checked, correlation ID generated → gRPC to Transaction Service → idempotency check (Redis double-checked lock + DB SELECT) → pre-generate `transaction_id` → gRPC to Risk Engine (with pre-generated UUID) → account profile loaded from Redis cache (DB fallback on miss) → 8 rules evaluated + 4 Redis velocity ops run concurrently → ML scoring via gRPC to ML Service (0.4–0.8ms ONNX inference) → 70/30 ensemble score → single DB INSERT at final status (no RECEIVED → UPDATE) → SQS event published → synchronous response returned. Async (SQS worker): upsert account profile, invalidate Redis profile cache, persist full RiskResult, optionally trigger LLM analyst for BLOCK/REVIEW.

**"Why pre-generate the UUID before inserting the transaction?"**
> The risk engine needs a `transaction_id` in the gRPC request so it can store the result under the right key. If you insert the row first (to get the DB-generated UUID), you hold a DB session open during the gRPC call — wasting a connection from the pool for ~25ms. Pre-generating with `uuid4()` lets you keep the idempotency SELECT and the INSERT as two separate short sessions, with scoring happening in between when no DB connection is held.

**"How do you prevent duplicate transactions?"**
> Three-layer idempotency: (1) Redis cache for sub-millisecond deduplication on retry storms (double-checked locking with NX SET), (2) DB unique constraint on `(idempotency_key, client_id)` as the authoritative source of truth, (3) 24-hour TTL on cached responses prevents unbounded Redis growth.

**"How does the ML model get updated without downtime?"**
> Admin triggers `POST /mlops/reload-model`. The ML Service's predictor singleton acquires a threading lock, fetches the new ONNX binary from S3, and atomically swaps the inference session. No TCP connections are dropped, no in-flight predictions are interrupted.

**"Why do you use a rules + ML ensemble instead of pure ML?"**
> Rules are deterministic, auditable, and immediately compliant with regulatory requirements. ML models can drift, produce false positives on underrepresented populations (e.g., new account types), and are opaque. Rules act as a hard compliance floor — the ML signal refines the decision, it does not own it. The 70/30 weighting reflects this: rules dominate.

**"How do you handle high availability for the fraud decision path?"**
> Every dependency has a fallback. Redis down → idempotency falls back to DB, velocity falls back to profile data. ML Service down → fallback score 0.0, rules decide. Risk Engine error → transaction defaults to REVIEW, never silently approved. The SQS acks-late pattern means no async work is lost if a worker crashes.

**"How is multi-tenancy enforced?"**
> Every Cognito JWT contains a `custom:tenant_id` claim set by a Lambda trigger at registration. The API Gateway middleware extracts this as `client_id` and passes it to all downstream services via gRPC metadata. Every DB query is filtered by `client_id`. Separate databases per service reinforce this — a bug in one service cannot leak data from another.

**"Why SQS instead of a message broker like Kafka?"**
> SQS is operationally simpler for this use case (at-least-once delivery, no consumer group management, no partition rebalancing). The workloads here are low-to-medium throughput (fraud decisions, not clickstream). SQS dead-letter queues handle poison messages automatically. For high-throughput analytics replay, Kafka would be the right call.

**"How does the LLM agent work?"**
> Two phases. Phase 1: a LlamaIndex ReActAgent runs a Thought → Action → Observation loop using 4 internal tools (sender profile, transaction patterns, risk decision inspection, IP intelligence) and produces a free-form investigation narrative. Phase 2: a focused instructor call converts that narrative into a validated `FraudInvestigationReport` Pydantic model — giving typed fields (`verdict`, `recommendation`, `confidence`, `risk_factors`) that the gRPC servicer and SQS worker access directly. instructor handles retry on validation failure automatically. The backend LLM is pluggable: Ollama, Anthropic, OpenAI, or Gemini, controlled by `LLM_PROVIDER` + `LLM_MODEL` in `.env`.

**"Why two phases instead of asking the agent to output JSON directly?"**
> Forcing structured JSON output from a ReActAgent breaks the tool-calling loop — the model fights between emitting tool-call format and emitting JSON. Separating concerns solves this cleanly: the agent reasons freely (Phase 1), then a dedicated single-shot extraction call (Phase 2) produces the validated model. instructor wraps this with automatic retry so the output is always schema-compliant before it reaches the rest of the code.

**"How would you swap from Ollama to Claude in production?"**
> Change two lines in `.env`: `LLM_PROVIDER=anthropic` and `LLM_MODEL=claude-sonnet-4-6`, add `ANTHROPIC_API_KEY`, rebuild the analyst-service container. Zero code changes. Both factories (`app/core/llm.py` for the agent loop, `app/core/structured_llm.py` for extraction) read the same env vars and validate the key at startup — misconfiguration is caught at deploy time, not mid-investigation.

---

## 14. Running the System Locally

```bash
# 1. Compile protobuf definitions
make proto

# 2. Start all services
docker-compose up -d --build

# 3. Seed the database with test personas
python generate_seed_data.py
cat seed_data.sql | docker exec -i postgres psql -U aegis

# 4. Access points
# Swagger UI:     http://localhost:8000/docs
# Login:          http://localhost:8000/auth/login
# Postgres:       localhost:5432
#   Databases:    aegis_risk, aegis_transactions, aegis_notifications
```

**Test personas (from seed data)**:
- **Client 1** — Mature account, consistent behavior → expect APPROVE
- **Client 2** — New account, high velocity, geo-hopping → expect BLOCK/REVIEW
