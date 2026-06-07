from abc import ABC, abstractmethod

from app.schemas.investigation import FraudInvestigationReport


class BaseAgentService(ABC):
    """Abstract interface for the AI Agent Service.

    Swap implementations (LlamaIndex, LangChain, plain SDK) without touching
    the worker or the gRPC servicer — they only depend on this interface.
    """

    @abstractmethod
    async def investigate_transaction(
        self, transaction_id: str, sender_id: str
    ) -> FraudInvestigationReport:
        """Run a full investigation and return a validated structured report."""
        pass

    @abstractmethod
    def get_agent_name(self) -> str:
        """Return a description of the implementation (for logging/DB)."""
        pass
