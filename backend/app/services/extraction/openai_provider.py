import json
from typing import Optional

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas import ExtractionResult
from app.services.extraction.interface import LLMProvider
from app.services.extraction.prompt import SYSTEM_PROMPT, build_user_message


class OpenAIProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.model = settings.llm_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def name(self) -> str:
        return f"openai/{self.model}"

    async def extract(self, enquiry_text: str) -> ExtractionResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(enquiry_text)},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content: Optional[str] = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned an empty response")
        payload = json.loads(content)
        return ExtractionResult.model_validate(payload)
