"""Concrete LlamaIndex ReAct agent implementation.

Uses Ollama (gemma3:12b) as the backing LLM and wires up the four
investigation tools.  Swap this file for a LangChain/LangGraph
implementation later — the rest of the service only depends on
the abstract `BaseAgentService` interface.
"""

import logging

from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context

from aegis_shared.utils.logging import get_logger

from app.config import settings
from app.services.base import BaseAgentService
from app.tools.agent_tools import get_all_tools
from app.core.llm import get_llm

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

Final Output: Your response MUST be a concise, structured fraud report.
You must speak in the first-person as an expert human analyst (e.g., "I investigated this transaction and found...").

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
SUMMARY: [A professional 2-3 sentence paragraph explaining your findings]
FACTORS:
- [Risk factor 1]
- [Risk factor 2]
VERDICT: [FRAUDULENT or LEGITIMATE or SUSPICIOUS]
RECOMMENDATION: [BLOCK or ALLOW or REVIEW]
"""


class LlamaIndexAgentService(BaseAgentService):
    """
    Implementation of the investigation service using LlamaIndex ReAct agent.
    """

    def __init__(self):
        # Initialize LLM via Factory
        self._llm = get_llm(timeout=120.0)

        # Initialize Tools
        self._tools = get_all_tools()

        # Initialize the Workflow-based ReActAgent
        # Note: In LlamaIndex 0.14+, from_tools() is deprecated in favor of direct constructor
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

    # ── BaseAgentService interface ────────────────────────────────────────────

    async def investigate_transaction(
        self, transaction_id: str, sender_id: str
    ) -> str:
        """Run a full fraud investigation and return the agent's report."""
        prompt = (
            f"Investigate this transaction for potential fraud.\n"
            f"Transaction ID: {transaction_id}\n"
            f"Sender ID: {sender_id}\n\n"
            f"Use every tool at your disposal, cross-reference the signals, "
            f"and give me your final verdict with evidence."
        )
        logger.info("investigate", transaction_id=transaction_id, sender_id=sender_id)
        
        # New LlamaIndex 0.14+ Workflow-based ReActAgent pattern
        # agent.run() returns a handler that we await for the final response
        try:
            handler = self._agent.run(prompt)
            response = await handler
            return str(response)
        except Exception as e:
            logger.error("agent_run_failed", transaction_id=transaction_id, error=str(e))
            raise

    def get_agent_name(self) -> str:
        return f"LlamaIndex ReAct Agent ({settings.LLM_MODEL})"
