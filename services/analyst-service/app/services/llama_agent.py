"""LlamaIndex ReAct agent implementation.

Two-phase approach:
  1. ReActAgent  — free-form reasoning loop using tools (unchanged)
  2. Structured extraction — one focused call via instructor/native SDK
     converts the agent's text into a validated FraudInvestigationReport

Swap the LLM provider by setting LLM_PROVIDER + LLM_MODEL in .env.
The rest of the service only depends on BaseAgentService.
"""

from aegis_shared.utils.logging import get_logger

from app.config import settings
from app.core.llm import get_llm
from app.core.structured_llm import extract_report
from app.schemas.investigation import FraudInvestigationReport
from app.services.base import BaseAgentService
from app.tools.agent_tools import get_all_tools

from llama_index.core.agent.workflow import ReActAgent

logger = get_logger("analyst-service.llama_agent")

_SYSTEM_PROMPT = """\
You are the Aegis Risk Investigator, a senior fraud analyst AI.
Your goal is to conduct a deep-dive investigation into a flagged transaction.
You have access to internal databases (profiles, transaction history) and external IP intelligence.

CRITICAL INSTRUCTIONS:
1. NEVER guess. If you need data, use a tool.
2. Search for Geo-velocity (physically impossible travel between transactions).
3. Search for Session Swaps (different devices or IPs for the same user).
4. Search for High-risk IP ranges (hosting providers, VPNs).
5. Compare the current amount to the sender's average behaviour.

Final Output: Write a detailed investigation narrative covering your findings,
the key risk signals you identified, your overall verdict, and your recommendation.
Be thorough — your output will be parsed into a structured report.
"""


class LlamaIndexAgentService(BaseAgentService):

    def __init__(self):
        self._llm = get_llm(timeout=120.0)
        self._tools = get_all_tools()
        self._agent = ReActAgent(
            tools=self._tools,
            llm=self._llm,
            system_prompt=_SYSTEM_PROMPT,
        )
        logger.info(
            "LlamaIndexAgentService initialised  provider=%s model=%s  tools=%d",
            settings.LLM_PROVIDER,
            settings.LLM_MODEL,
            len(self._tools),
        )

    async def investigate_transaction(
        self, transaction_id: str, sender_id: str
    ) -> FraudInvestigationReport:
        prompt = (
            f"Investigate this transaction for potential fraud.\n"
            f"Transaction ID: {transaction_id}\n"
            f"Sender ID: {sender_id}\n\n"
            f"Use every tool at your disposal, cross-reference the signals, "
            f"and give me your full findings."
        )
        logger.info("investigate_start", transaction_id=transaction_id, sender_id=sender_id)

        # Phase 1: agent reasoning loop (tool calls, free-form text)
        handler = self._agent.run(prompt)
        raw_text = str(await handler)

        logger.info(
            "agent_raw_output_received",
            transaction_id=transaction_id,
            output_length=len(raw_text),
        )

        # Phase 2: structured extraction — instructor validates the Pydantic model,
        # retrying if the provider returns malformed output
        report = await extract_report(raw_text)

        logger.info(
            "structured_report_extracted",
            transaction_id=transaction_id,
            verdict=report.verdict,
            recommendation=report.recommendation,
            confidence=report.confidence,
        )
        return report

    def get_agent_name(self) -> str:
        return f"LlamaIndex ReAct ({settings.LLM_PROVIDER}/{settings.LLM_MODEL})"
