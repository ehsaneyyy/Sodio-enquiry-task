from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ServiceLine(str, Enum):
    ai = "ai"
    blockchain = "blockchain"
    web = "web"
    mobile = "mobile"
    game = "game"
    other = "other"


class EnquiryStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    dropped = "dropped"


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ExtractionStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failed = "failed"


class TimelineUrgency(str, Enum):
    asap = "asap"
    near = "near"
    later = "later"
    flexible = "flexible"
    unknown = "unknown"


class BudgetUnit(str, Enum):
    base = "base"
    thousand = "thousand"
    lakh = "lakh"
    crore = "crore"
    million = "million"
    billion = "billion"


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    service_line: Optional[ServiceLine] = None
    budget_raw: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    budget_currency: Optional[str] = None
    budget_unit: BudgetUnit = BudgetUnit.base
    timeline: Optional[str] = None
    timeline_urgency: Optional[TimelineUrgency] = None
    summary: Optional[str] = None
    is_genuine: Optional[bool] = None


class CreateEnquiryRequest(BaseModel):
    original_text: str = Field(min_length=1, max_length=100_000)


class PatchEnquiryRequest(BaseModel):
    status: Optional[EnquiryStatus] = None
    overrides: Optional[dict[str, Any]] = None


class EnquiryListItem(BaseModel):
    id: int
    status: str
    priority: str
    extraction_status: str
    source: str
    created_at: Any
    overridden_fields: list[str]
    company: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    service_line: Optional[str] = None
    budget_raw: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    budget_currency: Optional[str] = None
    timeline: Optional[str] = None
    summary: Optional[str] = None
    is_genuine: Optional[bool] = None


class ExtractionRunResponse(BaseModel):
    id: int
    created_at: Any
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    company: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    service_line: Optional[str] = None
    budget_raw: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    budget_currency: Optional[str] = None
    timeline: Optional[str] = None
    timeline_urgency: Optional[str] = None
    summary: Optional[str] = None
    is_genuine: Optional[bool] = None
    error: Optional[str] = None


class EnquiryDetailResponse(BaseModel):
    id: int
    original_text: str
    source: str
    status: str
    priority: str
    extraction_status: str
    extraction_error: Optional[str] = None
    created_at: Any
    updated_at: Any
    overridden_fields: list[str]
    effective: EnquiryListItem
    latest_extraction: Optional[ExtractionRunResponse] = None
    extraction_history: list[ExtractionRunResponse] = []


class BatchItemResponse(BaseModel):
    enquiry_id: int
    extraction_status: str
    error: Optional[str] = None


class BatchDetailResponse(BaseModel):
    id: int
    filename: Optional[str] = None
    status: str
    total: int
    completed_count: int
    failed_count: int
    pending_count: int
    processing_count: int
    items: list[BatchItemResponse]


class BatchCreatedResponse(BaseModel):
    batch_id: int
    enquiry_ids: list[int]
    total: int
