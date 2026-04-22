from abc import ABC, abstractmethod

class BaseAgentService(ABC):
    """
    Abstract interface for the AI Agent Service to ensure loose coupling.
    This allows switching from LlamaIndex to LangChain or LangGraph easily later.
    """

    @abstractmethod
    async def investigate_transaction(self, transaction_id: str, sender_id: str) -> str:
        """
        Takes a transaction and sender id, performs a full investigation using
        available tools, and returns a detailed report on whether it thinks
        the transaction is fraudulent or legitimate.
        """
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the name or description of the implementation."""
        pass
