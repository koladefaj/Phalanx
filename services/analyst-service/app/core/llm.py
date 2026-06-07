"""LLM provider factory.

Set LLM_PROVIDER and LLM_MODEL in .env — no code changes needed to switch providers.

Supported providers
-------------------
  ollama      Local inference via Ollama (default, no API key needed)
  anthropic   Anthropic Claude  — requires ANTHROPIC_API_KEY
  openai      OpenAI GPT        — requires OPENAI_API_KEY
  gemini      Google Gemini     — requires GEMINI_API_KEY
"""

import logging

from app.config import settings

logger = logging.getLogger("llm_factory")

# Sensible per-provider defaults if LLM_MODEL is not explicitly set
_DEFAULT_MODELS = {
    "ollama": "gemma3:4b",
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o-mini",
    "gemini": "models/gemini-2.0-flash",
}


def _require_key(key_value: str | None, env_var: str, provider: str) -> str:
    if not key_value:
        raise ValueError(
            f"LLM_PROVIDER is set to '{provider}' but {env_var} is not configured. "
            f"Add {env_var}=<your-key> to your .env file."
        )
    return key_value


def get_llm(timeout: float = 120.0, **kwargs):
    """Instantiate and return a LlamaIndex-compatible LLM for the configured provider."""
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL or _DEFAULT_MODELS.get(provider, "")

    if provider == "ollama":
        from llama_index.llms.ollama import Ollama

        logger.info("llm_provider=ollama model=%s base_url=%s", model, settings.LLM_BASE_URL)
        return Ollama(
            model=model,
            base_url=settings.LLM_BASE_URL,
            request_timeout=timeout,
            **kwargs,
        )

    elif provider == "anthropic":
        from llama_index.llms.anthropic import Anthropic

        api_key = _require_key(settings.ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY", provider)
        logger.info("llm_provider=anthropic model=%s", model)
        return Anthropic(
            model=model,
            api_key=api_key,
            max_tokens=4096,
            **kwargs,
        )

    elif provider == "openai":
        from llama_index.llms.openai import OpenAI

        api_key = _require_key(settings.OPENAI_API_KEY, "OPENAI_API_KEY", provider)
        logger.info("llm_provider=openai model=%s", model)
        return OpenAI(
            model=model,
            api_key=api_key,
            **kwargs,
        )

    elif provider == "gemini":
        from llama_index.llms.gemini import Gemini

        api_key = _require_key(settings.GEMINI_API_KEY, "GEMINI_API_KEY", provider)
        logger.info("llm_provider=gemini model=%s", model)
        return Gemini(
            model_name=model,
            api_key=api_key,
            **kwargs,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            f"Valid options: ollama, anthropic, openai, gemini"
        )
