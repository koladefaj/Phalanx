"""Structured extraction layer — converts raw agent text into FraudInvestigationReport.

Each provider uses the best available structured output mechanism:
  anthropic  →  instructor.from_anthropic  (tool use, Anthropic's native mechanism)
  openai     →  instructor.from_openai     (json_schema response_format)
  gemini     →  instructor.from_gemini     (Gemini JSON mode)
  ollama     →  instructor.from_openai     (OpenAI-compat endpoint, JSON mode)

The agent's free-form reasoning output is passed to a single focused extraction call.
instructor retries automatically if the model returns invalid JSON or fails validation.
"""

import asyncio
import logging

import instructor

from app.config import settings
from app.schemas.investigation import FraudInvestigationReport

logger = logging.getLogger("structured_llm")

_EXTRACTION_PROMPT = """\
Below is a fraud investigation report produced by an AI analyst.
Extract the structured fields exactly as described in the report.
Do not invent information — if a field is ambiguous, use the closest match from the report.

For confidence: use 0.9 for very clear fraud/legitimacy signals, 0.65 for moderate suspicion, 0.35 for weak signals.

<report>
{report}
</report>
"""


async def extract_report(raw_text: str) -> FraudInvestigationReport:
    """Convert raw agent output into a validated FraudInvestigationReport."""
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL

    if provider == "anthropic":
        return await _extract_anthropic(raw_text, model, settings.ANTHROPIC_API_KEY)
    elif provider == "openai":
        return await _extract_openai(raw_text, model, settings.OPENAI_API_KEY)
    elif provider == "gemini":
        return await _extract_gemini(raw_text, model, settings.GEMINI_API_KEY)
    elif provider == "ollama":
        return await _extract_ollama(raw_text, model, settings.LLM_BASE_URL)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER for structured extraction: '{provider}'")


# ── Provider implementations ─────────────────────────────────────────────────

async def _extract_anthropic(
    raw_text: str, model: str, api_key: str
) -> FraudInvestigationReport:
    import anthropic

    client = instructor.from_anthropic(anthropic.AsyncAnthropic(api_key=api_key))
    return await client.messages.create(
        model=model,
        max_tokens=1024,
        response_model=FraudInvestigationReport,
        messages=[{"role": "user", "content": _EXTRACTION_PROMPT.format(report=raw_text)}],
    )


async def _extract_openai(
    raw_text: str, model: str, api_key: str
) -> FraudInvestigationReport:
    import openai

    client = instructor.from_openai(openai.AsyncOpenAI(api_key=api_key))
    return await client.chat.completions.create(
        model=model,
        response_model=FraudInvestigationReport,
        messages=[{"role": "user", "content": _EXTRACTION_PROMPT.format(report=raw_text)}],
    )


async def _extract_gemini(
    raw_text: str, model: str, api_key: str
) -> FraudInvestigationReport:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    gemini_client = genai.GenerativeModel(model_name=model)
    patched = instructor.from_gemini(gemini_client, mode=instructor.Mode.GEMINI_JSON)

    # google-generativeai is synchronous — run in thread pool to avoid blocking
    return await asyncio.to_thread(
        patched.chat.completions.create,
        response_model=FraudInvestigationReport,
        messages=[{"role": "user", "content": _EXTRACTION_PROMPT.format(report=raw_text)}],
    )


async def _extract_ollama(
    raw_text: str, model: str, base_url: str
) -> FraudInvestigationReport:
    import openai

    # Ollama exposes an OpenAI-compatible endpoint; JSON mode is more reliable
    # than function_call for smaller local models.
    client = instructor.from_openai(
        openai.AsyncOpenAI(base_url=f"{base_url}/v1", api_key="ollama"),
        mode=instructor.Mode.JSON,
    )
    return await client.chat.completions.create(
        model=model,
        response_model=FraudInvestigationReport,
        messages=[{"role": "user", "content": _EXTRACTION_PROMPT.format(report=raw_text)}],
    )
