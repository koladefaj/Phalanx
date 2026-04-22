"""LlamaIndex FunctionTools for the Aegis ReAct Fraud Investigation Agent.

Each tool queries a specific data source (DB or external API) and returns
a human-readable string the agent can reason over.
"""

import httpx
from sqlalchemy import select

from llama_index.core.tools import FunctionTool

from app.db.session import get_session
from app.models.read_only import (
    AccountProfileReadOnly,
    TransactionReadOnly,
    RiskResultReadOnly,
)


# ── Tool 1: Behavioral Baseline ──────────────────────────────────────────────

async def get_sender_profile(sender_id: str) -> str:
    """
    Fetches the lifetime and rolling-window behaviour for a sender.
    Returns avg_amount, total_txn_count, fraud_rate, account_age,
    velocity counters, and behavioural flags so you can judge whether
    the current transaction is 'normal' for this specific user.
    """
    async with get_session() as session:
        result = await session.execute(
            select(AccountProfileReadOnly)
            .where(AccountProfileReadOnly.account_id == sender_id)
        )
        profile = result.scalar_one_or_none()

    if not profile:
        return (
            f"No account profile found for sender_id: {sender_id}. "
            "This user has no prior transaction history — they may be brand-new."
        )

    return (
        f"Sender Profile for {sender_id}:\n"
        f"  Lifetime Transactions : {profile.total_txn_count}\n"
        f"  Lifetime Volume       : {profile.total_volume_lifetime}\n"
        f"  Avg Transaction Amount : {profile.avg_txn_amount}\n"
        f"  Max Transaction Amount : {profile.max_txn_amount}\n"
        f"  Last Transaction Amount: {profile.last_txn_amount}\n"
        f"  30-day Volume / Count  : {profile.total_volume_30d} / {profile.txn_count_30d}\n"
        f"  24-hour Volume / Count : {profile.total_volume_24h} / {profile.txn_count_24h}\n"
        f"  1-hour  Volume / Count : {profile.total_volume_1h} / {profile.txn_count_1h}\n"
        f"  Fraud Rate             : {profile.fraud_rate:.2f}%\n"
        f"  Fraud / Blocked / Review Txns: {profile.fraud_txn_count} / {profile.blocked_txn_count} / {profile.review_txn_count}\n"
        f"  Is High Risk           : {profile.is_high_risk}\n"
        f"  Unique Receivers       : {profile.unique_receiver_count}\n"
        f"  Unique Devices         : {profile.unique_device_count}\n"
        f"  Unique Countries       : {profile.unique_country_count}\n"
        f"  First Seen             : {profile.first_seen_at}\n"
        f"  Last Seen              : {profile.last_seen_at}"
    )


# ── Tool 2: Pattern Hunter ───────────────────────────────────────────────────

async def fetch_recent_transaction_patterns(sender_id: str, limit: int = 10) -> str:
    """
    Retrieves the last N transactions for a sender to analyse
    IP addresses, device fingerprints, countries, and timing gaps.
    Use this to detect session swaps, velocity spikes, or geo-hopping.
    """
    async with get_session() as session:
        result = await session.execute(
            select(TransactionReadOnly)
            .where(TransactionReadOnly.sender_id == sender_id)
            .order_by(TransactionReadOnly.created_at.desc())
            .limit(limit)
        )
        txns = result.scalars().all()

    if not txns:
        return f"No prior transactions found for sender_id: {sender_id}."

    lines = [f"Last {len(txns)} transactions for {sender_id}:\n"]
    for t in txns:
        lines.append(
            f"  [{t.transaction_id}] {t.created_at}  "
            f"Amount={t.amount} {t.currency}  "
            f"IP={t.ip_address}  Device={t.device_fingerprint}  "
            f"SenderCountry={t.sender_country}  ReceiverCountry={t.receiver_country}  "
            f"Channel={t.channel}  Status={t.status}"
        )
    return "\n".join(lines)


# ── Tool 3: Decision Auditor ─────────────────────────────────────────────────

async def inspect_automated_decision(transaction_id: str) -> str:
    """
    Retrieves the full risk-engine output for a transaction: the ML
    anomaly score, triggered rules, rule flags, overall risk score,
    risk level, decision, and any LLM explanation that was generated.
    Use this to understand WHY the system blocked or flagged a transaction.
    """
    async with get_session() as session:
        result = await session.execute(
            select(RiskResultReadOnly)
            .where(RiskResultReadOnly.transaction_id == transaction_id)
        )
        rr = result.scalar_one_or_none()

    if not rr:
        return f"No risk result found for transaction_id: {transaction_id}."

    triggered = ", ".join(rr.triggered_rules) if rr.triggered_rules else "None"
    agent_factors = ", ".join(rr.agent_risk_factors) if rr.agent_risk_factors else "N/A"

    return (
        f"Risk Engine Decision for transaction {transaction_id}:\n"
        f"  Overall Risk Score : {rr.risk_score}\n"
        f"  Risk Level         : {rr.risk_level}\n"
        f"  Decision           : {rr.decision}\n"
        f"  Confidence         : {rr.confidence}\n"
        f"  Rule Score         : {rr.rule_score}\n"
        f"  Triggered Rules    : {triggered}\n"
        f"  Rule Flags         : {rr.rule_flags}\n"
        f"  ML Anomaly Score   : {rr.ml_anomaly_score}\n"
        f"  ML Model Version   : {rr.ml_model_version}\n"
        f"  ML Fallback Used   : {rr.ml_fallback_used}\n"
        f"  Agent Summary      : {rr.agent_summary or 'Not yet available'}\n"
        f"  Agent Risk Factors : {agent_factors}\n"
        f"  Agent Recommendation: {rr.agent_recommendation or 'N/A'}\n"
        f"  Evaluated At       : {rr.evaluated_at}"
    )


# ── Tool 4: External IP Intelligence ─────────────────────────────────────────

async def get_ip_intelligence(ip_address: str) -> str:
    """
    Performs a geo-lookup and risk-check on an IP address using ip-api.com.
    Checks for VPN/Proxy/TOR exit nodes and Data Center ranges.
    A 'hosting' flag means the IP belongs to a cloud provider (likely bot/VPN).
    """
    if not ip_address or ip_address in ("127.0.0.1", "localhost", "0.0.0.0"):
        return f"IP {ip_address} is local/internal — no external intelligence available."

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip_address}",
                params={
                    "fields": "status,message,country,city,isp,org,as,mobile,proxy,hosting",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") == "fail":
            return f"IP lookup failed for {ip_address}: {data.get('message')}"

        flags: list[str] = []
        if data.get("hosting"):
            flags.append("⚠ Data-Center / Hosting Provider (high bot/VPN risk)")
        if data.get("proxy"):
            flags.append("⚠ Known Proxy / VPN / Tor exit node")
        if not flags:
            flags.append("Clean residential / mobile IP")

        return (
            f"IP Intelligence for {ip_address}:\n"
            f"  Country      : {data.get('country')}\n"
            f"  City         : {data.get('city')}\n"
            f"  ISP          : {data.get('isp')}\n"
            f"  Organisation : {data.get('org')}\n"
            f"  AS           : {data.get('as')}\n"
            f"  Mobile       : {data.get('mobile')}\n"
            f"  Risk Flags   : {' | '.join(flags)}"
        )

    except Exception as exc:
        return f"External IP lookup failed for {ip_address}: {exc}"


# ── Register all tools ────────────────────────────────────────────────────────

def get_all_tools() -> list[FunctionTool]:
    """Return the full toolkit for the ReAct agent."""
    return [
        FunctionTool.from_defaults(async_fn=get_sender_profile, name="get_sender_profile", description="Fetch the lifetime behavioural profile of a sender account."),
        FunctionTool.from_defaults(async_fn=fetch_recent_transaction_patterns, name="fetch_recent_transaction_patterns", description="Retrieve the last N transactions for a sender to spot IP/device/geo anomalies."),
        FunctionTool.from_defaults(async_fn=inspect_automated_decision, name="inspect_automated_decision", description="Retrieve the risk engine's full scoring output for a specific transaction."),
        FunctionTool.from_defaults(async_fn=get_ip_intelligence, name="get_ip_intelligence", description="Perform an external geo and risk lookup on an IP address."),
    ]
