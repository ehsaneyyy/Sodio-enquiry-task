from abc import ABC, abstractmethod

from app.schemas import ExtractionResult


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def extract(self, enquiry_text: str) -> ExtractionResult:
        raise NotImplementedError
