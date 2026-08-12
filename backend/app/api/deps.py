from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.extraction.factory import build_provider
from app.services.extraction.interface import LLMProvider


def get_llm_provider(settings: Settings = Depends(get_settings)) -> LLMProvider:
    return build_provider(settings)
