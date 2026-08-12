from typing import Optional

from app.core.config import Settings, get_settings
from app.services.extraction.interface import LLMProvider
from app.services.extraction.openai_provider import OpenAIProvider
from app.services.extraction.stub_provider import StubProvider


def build_provider(settings: Optional[Settings] = None) -> LLMProvider:
    resolved_settings = settings if settings is not None else get_settings()
    if resolved_settings.llm_provider == "openai":
        if not resolved_settings.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set")
        return OpenAIProvider(resolved_settings)
    return StubProvider()
