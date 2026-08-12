import re
from typing import Any, Optional

from app.models import Enquiry, Extraction
from app.schemas import TimelineUrgency

OVERRIDABLE_FIELDS = [
    "company",
    "contact_name",
    "contact_email",
    "service_line",
    "budget_raw",
    "budget_min",
    "budget_max",
    "budget_currency",
    "timeline",
    "summary",
    "is_genuine",
]

ASAP_WORDS = ["asap", "immediate", "as soon", "now", "today", "urgent", "emergency", "tonight", "this week", "next week"]
FLEXIBLE_WORDS = ["flexible", "tbd", "whenever", "open-ended", "not finalised", "not yet"]
LATER_WORDS = ["next year", "q3", "q4", "eighteen", "phased", "milestone"]
NEAR_WORDS = ["week", "month", "q1", "q2", "before", "by ", "quarter", "this year", "september", "october", "november", "december"]


def _word_boundary_pattern(word: str) -> str:
    return rf"\b{re.escape(word)}\b"


def infer_urgency_from_timeline(timeline_text: Optional[str]) -> Optional[TimelineUrgency]:
    if not timeline_text:
        return None
    normalized = timeline_text.lower()
    for word in ASAP_WORDS:
        if re.search(_word_boundary_pattern(word), normalized):
            return TimelineUrgency.asap
    for word in FLEXIBLE_WORDS:
        if re.search(_word_boundary_pattern(word), normalized):
            return TimelineUrgency.flexible
    for word in LATER_WORDS:
        if re.search(_word_boundary_pattern(word), normalized):
            return TimelineUrgency.later
    for word in NEAR_WORDS:
        if re.search(_word_boundary_pattern(word), normalized):
            return TimelineUrgency.near
    return TimelineUrgency.unknown


def list_overridden_fields(enquiry: Enquiry) -> list[str]:
    return [field for field in OVERRIDABLE_FIELDS if getattr(enquiry, f"{field}_override") is not None]


def resolve_effective_values(enquiry: Enquiry, extraction: Optional[Extraction]) -> dict[str, Any]:
    effective: dict[str, Any] = {}
    for field in OVERRIDABLE_FIELDS:
        override_value = getattr(enquiry, f"{field}_override")
        extraction_value = getattr(extraction, field) if extraction is not None else None
        effective[field] = override_value if override_value is not None else extraction_value
    if enquiry.timeline_override is not None:
        effective["timeline_urgency"] = infer_urgency_from_timeline(enquiry.timeline_override)
    else:
        effective["timeline_urgency"] = getattr(extraction, "timeline_urgency", None) if extraction is not None else None
    return effective
