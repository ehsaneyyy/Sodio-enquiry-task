from typing import Any, Optional

from app.models import Enquiry, Extraction
from app.schemas import (
    EnquiryDetailResponse,
    EnquiryListItem,
    ExtractionRunResponse,
)
from app.services.effective import list_overridden_fields


def build_enquiry_list_item(enquiry: Enquiry, effective_values: dict[str, Any]) -> EnquiryListItem:
    return EnquiryListItem(
        id=enquiry.id,
        status=enquiry.status,
        priority=enquiry.priority,
        extraction_status=enquiry.extraction_status,
        source=enquiry.source,
        created_at=enquiry.created_at,
        overridden_fields=list_overridden_fields(enquiry),
        company=effective_values.get("company"),
        contact_name=effective_values.get("contact_name"),
        contact_email=effective_values.get("contact_email"),
        service_line=effective_values.get("service_line"),
        budget_raw=effective_values.get("budget_raw"),
        budget_min=effective_values.get("budget_min"),
        budget_max=effective_values.get("budget_max"),
        budget_currency=effective_values.get("budget_currency"),
        timeline=effective_values.get("timeline"),
        summary=effective_values.get("summary"),
        is_genuine=effective_values.get("is_genuine"),
    )


def build_extraction_run_response(extraction: Optional[Extraction]) -> Optional[ExtractionRunResponse]:
    if extraction is None:
        return None
    return ExtractionRunResponse(
        id=extraction.id,
        created_at=extraction.created_at,
        model=extraction.model,
        prompt_version=extraction.prompt_version,
        company=extraction.company,
        contact_name=extraction.contact_name,
        contact_email=extraction.contact_email,
        service_line=extraction.service_line,
        budget_raw=extraction.budget_raw,
        budget_min=extraction.budget_min,
        budget_max=extraction.budget_max,
        budget_currency=extraction.budget_currency,
        timeline=extraction.timeline,
        timeline_urgency=extraction.timeline_urgency,
        summary=extraction.summary,
        is_genuine=extraction.is_genuine,
        error=extraction.error,
    )


def build_enquiry_detail_response(
    enquiry: Enquiry,
    effective_values: dict[str, Any],
    extraction_history: list[Extraction],
) -> EnquiryDetailResponse:
    latest_extraction = extraction_history[-1] if extraction_history else None
    return EnquiryDetailResponse(
        id=enquiry.id,
        original_text=enquiry.original_text,
        source=enquiry.source,
        status=enquiry.status,
        priority=enquiry.priority,
        extraction_status=enquiry.extraction_status,
        extraction_error=enquiry.extraction_error,
        created_at=enquiry.created_at,
        updated_at=enquiry.updated_at,
        overridden_fields=list_overridden_fields(enquiry),
        effective=build_enquiry_list_item(enquiry, effective_values),
        latest_extraction=build_extraction_run_response(latest_extraction),
        extraction_history=[build_extraction_run_response(extraction) for extraction in extraction_history],
    )
