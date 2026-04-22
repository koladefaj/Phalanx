"""LLM Factory for loose coupling of the language model provider."""

import logging
from app.config import settings

logger = logging.getLogger("llm_factory")

def get_llm(timeout: float = 120.0, **kwargs):
    """Factory function to instantiate the configured LLM provider.
    
    Supports loose coupling so Aegis Risk can seamlessly switch between
    Ollama (local/edge), Gemini, OpenAI, or Anthropic.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        from llama_index.llms.ollama import Ollama
        
        logger.info(f"Instantiating Ollama LLM (model={settings.LLM_MODEL})")
        return Ollama(
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL,
            request_timeout=timeout,
            **kwargs
        )
        
    elif provider == "gemini":
        from llama_index.llms.gemini import Gemini
        
        logger.info(f"Instantiating Gemini LLM (model={settings.LLM_MODEL})")
        return Gemini(
            model=settings.LLM_MODEL,
            api_key=settings.GEMINI_API_KEY,
            **kwargs
        )
        
    elif provider == "openai":
        from llama_index.llms.openai import OpenAI
        
        logger.info(f"Instantiating OpenAI LLM (model={settings.LLM_MODEL})")
        return OpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            **kwargs
        )
        
    elif provider == "anthropic":
        from llama_index.llms.anthropic import Anthropic
        
        logger.info(f"Instantiating Anthropic LLM (model={settings.LLM_MODEL})")
        return Anthropic(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            **kwargs
        )
        
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
