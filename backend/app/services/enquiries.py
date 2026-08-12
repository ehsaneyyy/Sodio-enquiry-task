from typing import Any, Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Enquiry, Extraction, utc_now
from app.schemas import ServiceLine
from app.services.budget import normalize_llm_budget, parse_budget_string
from app.services.effective import OVERRIDABLE_FIELDS, resolve_effective_values
from app.services.extraction.interface import LLMProvider
from app.services.scoring import compute_priority

SIMPLE_OVERRIDE_KEYS = {
    "company": "company",
    "contact_name": "contact_name",
    "contact_email": "contact_email",
    "service_line": "service_line",
    "timeline": "timeline",
    "summary": "summary",
    "is_genuine": "is_genuine",
}

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


async def apply_overrides(enquiry: Enquiry, overrides: dict[str, Any]) -> None:
    for key, value in overrides.items():
        if key == "budget":
            _apply_budget_override(enquiry, value)
            continue
        field_name = SIMPLE_OVERRIDE_KEYS.get(key)
        if field_name is None:
            raise ValueError(f"Unknown override field: {key}")
        if key == "service_line" and value is not None:
            ServiceLine(value)
        if key == "is_genuine" and value is not None and not isinstance(value, bool):
            raise ValueError("is_genuine must be a boolean or null")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{key} must be a string or null")
        setattr(enquiry, f"{field_name}_override", value)


def _apply_budget_override(enquiry: Enquiry, value: Any) -> None:
    if value is None:
        enquiry.budget_raw_override = None
        enquiry.budget_min_override = None
        enquiry.budget_max_override = None
        enquiry.budget_currency_override = None
        return
    raw_budget = str(value)
    budget_min, budget_max, budget_currency = parse_budget_string(raw_budget)
    enquiry.budget_raw_override = raw_budget
    enquiry.budget_min_override = budget_min
    enquiry.budget_max_override = budget_max
    enquiry.budget_currency_override = budget_currency


async def recompute_priority(session: AsyncSession, enquiry: Enquiry) -> None:
    latest_extraction = None
    if enquiry.last_extraction_id is not None:
        latest_extraction = await session.get(Extraction, enquiry.last_extraction_id)
    effective_values = resolve_effective_values(enquiry, latest_extraction)
    enquiry.priority = compute_priority(effective_values).value
    enquiry.updated_at = utc_now()


async def run_extraction(
    session: AsyncSession,
    enquiry: Enquiry,
    provider: LLMProvider,
    model_name: str,
    prompt_version: str,
) -> None:
    enquiry.extraction_status = "processing"
    enquiry.extraction_error = None
    await session.flush()
    try:
        result = await provider.extract(enquiry.original_text)
    except Exception as exc:
        enquiry.extraction_status = "failed"
        enquiry.extraction_error = str(exc)
        await session.commit()
        return
    budget_min, budget_max, budget_currency = normalize_llm_budget(
        result.budget_min, result.budget_max, result.budget_currency, result.budget_unit
    )
    if budget_min is None and result.budget_raw:
        parsed_min, parsed_max, parsed_currency = parse_budget_string(result.budget_raw)
        budget_min = budget_min if budget_min is not None else parsed_min
        budget_max = budget_max if budget_max is not None else parsed_max
        budget_currency = budget_currency or parsed_currency
    extraction = Extraction(
        enquiry_id=enquiry.id,
        model=model_name,
        prompt_version=prompt_version,
        company=result.company,
        contact_name=result.contact_name,
        contact_email=result.contact_email,
        service_line=result.service_line.value if result.service_line else None,
        budget_raw=result.budget_raw,
        budget_min=budget_min,
        budget_max=budget_max,
        budget_currency=budget_currency,
        timeline=result.timeline,
        timeline_urgency=result.timeline_urgency.value if result.timeline_urgency else None,
        summary=result.summary,
        is_genuine=result.is_genuine,
    )
    session.add(extraction)
    await session.flush()
    enquiry.last_extraction_id = extraction.id
    enquiry.extraction_status = "success"
    await recompute_priority(session, enquiry)
    await session.commit()


async def create_enquiry(
    session: AsyncSession,
    original_text: str,
    source: str,
    provider: LLMProvider,
    model_name: str,
    prompt_version: str,
) -> Enquiry:
    enquiry = Enquiry(original_text=original_text, source=source)
    session.add(enquiry)
    await session.flush()
    await run_extraction(session, enquiry, provider, model_name, prompt_version)
    return enquiry


async def list_enquiries(
    session: AsyncSession,
    service_line: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "date",
) -> list[tuple[Enquiry, dict[str, Any]]]:
    enquiries = list((await session.exec(select(Enquiry))).all())
    latest_by_id = await _latest_extraction_map(session, [enquiry.id for enquiry in enquiries])
    entries: list[tuple[Enquiry, dict[str, Any]]] = []
    for enquiry in enquiries:
        latest_extraction = latest_by_id.get(enquiry.id)
        effective_values = resolve_effective_values(enquiry, latest_extraction)
        entries.append((enquiry, effective_values))
    if service_line:
        entries = [entry for entry in entries if entry[1].get("service_line") == service_line]
    if priority:
        entries = [entry for entry in entries if entry[0].priority == priority]
    if status:
        entries = [entry for entry in entries if entry[0].status == status]
    if sort == "priority":
        entries.sort(key=lambda entry: (PRIORITY_RANK.get(entry[0].priority, 9), -entry[0].created_at.timestamp()))
    else:
        entries.sort(key=lambda entry: entry[0].created_at, reverse=True)
    return entries


async def _latest_extraction_map(session: AsyncSession, enquiry_ids: list[int]) -> dict[int, Extraction]:
    if not enquiry_ids:
        return {}
    extractions = list(
        (await session.exec(select(Extraction).where(Extraction.enquiry_id.in_(enquiry_ids)))).all()
    )
    latest: dict[int, Extraction] = {}
    for extraction in extractions:
        current = latest.get(extraction.enquiry_id)
        if current is None or extraction.created_at > current.created_at:
            latest[extraction.enquiry_id] = extraction
    return latest


async def get_enquiry_detail(session: AsyncSession, enquiry_id: int) -> tuple[Optional[Enquiry], list[Extraction]]:
    enquiry = await session.get(Enquiry, enquiry_id)
    if enquiry is None:
        return None, []
    history = list(
        (
            await session.exec(
                select(Extraction).where(Extraction.enquiry_id == enquiry_id).order_by(Extraction.created_at)
            )
        ).all()
    )
    return enquiry, history


async def reset_overrides(session: AsyncSession, enquiry: Enquiry) -> None:
    for field_name in OVERRIDABLE_FIELDS:
        setattr(enquiry, f"{field_name}_override", None)
    await recompute_priority(session, enquiry)
    await session.commit()
