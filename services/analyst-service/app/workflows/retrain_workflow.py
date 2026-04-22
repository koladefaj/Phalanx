"""Aegis MLOps Retraining Workflow — LlamaIndex Workflow pattern.

Architecture:
  StartEvent
      │
      ▼
  monitor_performance()   ← queries risk_results table for live metrics
      │
      ▼
  analyze_and_decide()    ← LLM interprets metrics, decides RETRAIN or HOLD
      │
  ┌───┴────────────┐
  ▼                ▼
execute_mlops()   StopEvent("model_healthy")
  │  (retrain + upload simulation)
  ▼
reload_model()    ← gRPC hot-swap signal to ml-service
  │
  ▼
StopEvent(result=<summary>)

Why Workflow instead of ReAct for this job:
  - Retraining is DETERMINISTIC — steps never change order.
  - ReAct is for open-ended "figure out what to do next" tasks.
  - Workflow gives you traceability: log exactly which step was in progress
    when a production retrain failed.
  - The LLM is used ONLY for interpretation (analyze_and_decide), not
    for controlling the pipeline — that's the right boundary.
"""

import uuid
from datetime import datetime, UTC
from typing import Union

from llama_index.core.workflow import (
    Workflow,
    step,
    StartEvent,
    StopEvent,
    Event,
)
from app.core.llm import get_llm

from aegis_shared.utils.logging import get_logger
from app.config import settings
from app.workflows.mlops_tools import (
    fetch_model_performance_metrics,
    run_local_retraining,
    simulate_model_upload,
    trigger_model_hot_swap,
)

logger = get_logger("retrain_workflow")


# ── Custom Events (the typed messages between steps) ─────────────────────────


class MetricsReadyEvent(Event):
    """Carries live performance metrics from Step 1 → Step 2."""

    metrics: dict
    run_id: str


class RetrainDecisionEvent(Event):
    """Carries the LLM's decision and reasoning from Step 2 → Step 3."""

    should_retrain: bool
    reasoning: str
    new_version: str
    metrics: dict
    run_id: str


class ArtifactsReadyEvent(Event):
    """Carries train results from Step 3 → Step 4."""

    new_version: str
    train_result: dict
    upload_result: dict
    run_id: str


# ── The Workflow ──────────────────────────────────────────────────────────────


class RetrainingWorkflow(Workflow):
    """
    LlamaIndex Workflow that monitors ML model performance and
    orchestrates retraining when the LLM decides it's necessary.

    Instantiate with a timeout (seconds) appropriate for your hardware:
        workflow = RetrainingWorkflow(timeout=300)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = get_llm(timeout=120.0)

    # ── Step 1: Collect metrics ───────────────────────────────────────────────

    @step
    async def monitor_performance(self, ev: StartEvent) -> MetricsReadyEvent:
        """
        Query the live risk_results table to compute model health signals.
        No LLM involved — pure DB aggregation.
        """
        run_id = str(uuid.uuid4())[:8]
        lookback = getattr(ev, "lookback_days", 7)

        logger.info("workflow_step_start", step="monitor_performance", run_id=run_id)

        metrics = await fetch_model_performance_metrics(lookback_days=lookback)

        logger.info(
            "metrics_collected",
            run_id=run_id,
            total_decisions=metrics["total_decisions"],
            block_rate=metrics["block_rate"],
            ml_fallback_rate=metrics["ml_fallback_rate"],
        )

        return MetricsReadyEvent(metrics=metrics, run_id=run_id)

    # ── Step 2: LLM analysis and decision ────────────────────────────────────

    @step
    async def analyze_and_decide(
        self, ev: MetricsReadyEvent
    ) -> Union[RetrainDecisionEvent, StopEvent]:
        """
        The only step where the LLM is involved.

        The model is given the live metrics and asked to reason about whether
        retraining is warranted — weighing false positive risk, drift signals,
        and ML fallback rate against the cost of a retrain.
        """
        logger.info("workflow_step_start", step="analyze_and_decide", run_id=ev.run_id)

        m = ev.metrics

        # Guard: if there's no real data yet, skip
        if m["total_decisions"] < 10:
            reason = (
                f"Insufficient data: only {m['total_decisions']} decisions "
                "in the lookback window. Need at least 10 to make a meaningful assessment."
            )
            logger.info(
                "workflow_skip_insufficient_data", run_id=ev.run_id, reason=reason
            )
            return StopEvent(result=reason)

        prompt = f"""You are an MLOps analyst for Aegis Risk, a real-time fraud detection system.

The XGBoost fraud detection model has been running in production. Here are the latest performance metrics from the past {m["lookback_days"]} days:

PERFORMANCE REPORT
==================
Total decisions evaluated : {m["total_decisions"]}
Block rate (flagged fraud) : {m["block_rate"]:.1%}
Review rate (uncertain)   : {m["review_rate"]:.1%}
Approve rate              : {m["approve_rate"]:.1%}
Average risk score        : {m["avg_risk_score"]:.3f}
High-risk proportion      : {m["high_risk_proportion"]:.1%}
ML fallback rate          : {m["ml_fallback_rate"]:.1%}  ← model unreachable or erroring
Agent investigation coverage: {m["agent_coverage"]:.1%}

DECISION CRITERIA
=================
- Retrain if: block_rate > 30% (too aggressive, likely false positives)
- Retrain if: ml_fallback_rate > 10% (model is unstable or outdated)  
- Retrain if: review_rate > 25% (model is uncertain too often — needs calibration)
- Retrain if: avg_risk_score > 0.7 (model is systematically over-scoring)
- Hold if: all metrics are within acceptable bounds

Your task:
1. Analyse these metrics critically.
2. Identify any concerning trends.
3. State clearly: DECISION: RETRAIN or DECISION: HOLD
4. In 2-3 sentences, explain your reasoning to the engineering team.

Respond in this exact format:
DECISION: <RETRAIN or HOLD>
REASONING: <your explanation>
"""

        response = await self.llm.acomplete(prompt)
        raw_text = str(response)

        logger.info(
            "llm_decision_received", run_id=ev.run_id, response_preview=raw_text[:200]
        )

        # Parse the LLM response
        should_retrain = (
            "RETRAIN" in raw_text.upper() and "DECISION: RETRAIN" in raw_text.upper()
        )
        reasoning = raw_text.strip()

        # Generate a semver-style version string
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M")
        new_version = f"v2.{ts}"

        if not should_retrain:
            logger.info(
                "workflow_hold_decision", run_id=ev.run_id, reasoning=reasoning[:100]
            )
            return StopEvent(
                result=f"Model performing within spec. No retrain triggered.\n\n{reasoning}"
            )

        logger.info(
            "workflow_retrain_decision", run_id=ev.run_id, new_version=new_version
        )
        return RetrainDecisionEvent(
            should_retrain=True,
            reasoning=reasoning,
            new_version=new_version,
            metrics=ev.metrics,
            run_id=ev.run_id,
        )

    # ── Step 3: Execute retraining + simulated upload ─────────────────────────

    @step
    async def execute_mlops(self, ev: RetrainDecisionEvent) -> ArtifactsReadyEvent:
        """
        Run the real XGBoost trainer and simulate an S3 artifact upload.

        trainer.py is executed in a thread pool so it doesn't block the event
        loop during the CPU-heavy sklearn/XGBoost fit() call.
        """
        logger.info(
            "workflow_step_start",
            step="execute_mlops",
            run_id=ev.run_id,
            new_version=ev.new_version,
        )

        # Run trainer.py (the real thing — no mocking)
        train_result = await run_local_retraining(ev.new_version)

        logger.info(
            "retraining_complete",
            run_id=ev.run_id,
            auc=train_result.get("auc"),
            threshold=train_result.get("threshold"),
        )

        # Simulate S3 upload (locally, artifacts are already on disk)
        upload_result = await simulate_model_upload(ev.new_version, train_result)

        return ArtifactsReadyEvent(
            new_version=ev.new_version,
            train_result=train_result,
            upload_result=upload_result,
            run_id=ev.run_id,
        )

    # ── Step 4: Hot-swap via gRPC ─────────────────────────────────────────────

    @step
    async def reload_model(self, ev: ArtifactsReadyEvent) -> StopEvent:
        """
        Signal the ml-service to reload the new ONNX model via gRPC.
        Zero downtime — the predictor swaps the model file atomically.
        """
        logger.info(
            "workflow_step_start",
            step="reload_model",
            run_id=ev.run_id,
            version=ev.new_version,
        )

        swap_result = await trigger_model_hot_swap(ev.new_version)

        summary = {
            "run_id": ev.run_id,
            "new_version": ev.new_version,
            "auc": ev.train_result.get("auc"),
            "threshold": ev.train_result.get("threshold"),
            "uploaded": ev.upload_result.get("simulated", False),
            "hot_swap": swap_result.get("reloaded", False),
            "completed_at": datetime.now(UTC).isoformat(),
        }

        logger.info("workflow_complete", **summary)

        return StopEvent(
            result=(
                f"   Retraining complete.\n"
                f"   Version  : {ev.new_version}\n"
                f"   AUC      : {ev.train_result.get('auc')}\n"
                f"   Threshold: {ev.train_result.get('threshold')}\n"
                f"   Hot-swap : {'Live' if swap_result.get('reloaded') else '⚠ Manual reload required'}\n"
            )
        )
