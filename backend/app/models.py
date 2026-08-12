from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Enquiry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_text: str
    source: str = "manual"
    status: str = "new"
    priority: str = "low"
    extraction_status: str = "pending"
    extraction_error: Optional[str] = None
    batch_id: Optional[int] = Field(default=None, foreign_key="batch.id", index=True)
    last_extraction_id: Optional[int] = Field(default=None, foreign_key="extraction.id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    company_override: Optional[str] = None
    contact_name_override: Optional[str] = None
    contact_email_override: Optional[str] = None
    service_line_override: Optional[str] = None
    budget_raw_override: Optional[str] = None
    budget_min_override: Optional[float] = None
    budget_max_override: Optional[float] = None
    budget_currency_override: Optional[str] = None
    timeline_override: Optional[str] = None
    summary_override: Optional[str] = None
    is_genuine_override: Optional[bool] = None


class Extraction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enquiry_id: int = Field(foreign_key="enquiry.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
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
    raw_model_output: Optional[str] = None
    error: Optional[str] = None


class Batch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: Optional[str] = None
    status: str = "processing"
    total: int = 0
    created_at: datetime = Field(default_factory=utc_now)
