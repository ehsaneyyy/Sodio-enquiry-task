from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_llm_provider
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.models import Enquiry
from app.schemas import (
    CreateEnquiryRequest,
    EnquiryDetailResponse,
    EnquiryListItem,
    EnquiryStatus,
    PatchEnquiryRequest,
    Priority,
    ServiceLine,
)
from app.services import enquiries as enquiries_service
from app.services.effective import resolve_effective_values
from app.services.extraction.interface import LLMProvider
from app.services.serializers import build_enquiry_detail_response, build_enquiry_list_item

router = APIRouter(prefix="/api/enquiries", tags=["enquiries"])


@router.post("", status_code=201, response_model=EnquiryDetailResponse)
async def create_enquiry_from_text(
    payload: CreateEnquiryRequest,
    session: AsyncSession = Depends(get_session),
    provider: LLMProvider = Depends(get_llm_provider),
    settings: Settings = Depends(get_settings),
) -> EnquiryDetailResponse:
    enquiry = await enquiries_service.create_enquiry(
        session, payload.original_text, "manual", provider, provider.name, settings.extraction_prompt_version
    )
    return await _build_detail(session, enquiry.id)


@router.get("", response_model=list[EnquiryListItem])
async def list_enquiries(
    service_line: Optional[ServiceLine] = None,
    priority: Optional[Priority] = None,
    status: Optional[EnquiryStatus] = None,
    sort: str = "date",
    session: AsyncSession = Depends(get_session),
) -> list[EnquiryListItem]:
    entries = await enquiries_service.list_enquiries(
        session,
        service_line=service_line.value if service_line else None,
        priority=priority.value if priority else None,
        status=status.value if status else None,
        sort=sort,
    )
    return [build_enquiry_list_item(enquiry, effective_values) for enquiry, effective_values in entries]


@router.get("/{enquiry_id}", response_model=EnquiryDetailResponse)
async def get_enquiry(
    enquiry_id: int,
    session: AsyncSession = Depends(get_session),
) -> EnquiryDetailResponse:
    return await _build_detail(session, enquiry_id)


@router.patch("/{enquiry_id}", response_model=EnquiryDetailResponse)
async def patch_enquiry(
    enquiry_id: int,
    payload: PatchEnquiryRequest,
    session: AsyncSession = Depends(get_session),
) -> EnquiryDetailResponse:
    enquiry = await session.get(Enquiry, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    if payload.status is not None:
        enquiry.status = payload.status.value
    if payload.overrides:
        try:
            await enquiries_service.apply_overrides(enquiry, payload.overrides)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
    await enquiries_service.recompute_priority(session, enquiry)
    await session.commit()
    return await _build_detail(session, enquiry_id)


@router.post("/{enquiry_id}/re-extract", response_model=EnquiryDetailResponse)
async def re_extract_enquiry(
    enquiry_id: int,
    session: AsyncSession = Depends(get_session),
    provider: LLMProvider = Depends(get_llm_provider),
    settings: Settings = Depends(get_settings),
) -> EnquiryDetailResponse:
    enquiry = await session.get(Enquiry, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    if enquiry.extraction_status == "processing":
        raise HTTPException(status_code=409, detail="Extraction is already in progress")
    await enquiries_service.run_extraction(
        session, enquiry, provider, provider.name, settings.extraction_prompt_version
    )
    return await _build_detail(session, enquiry_id)


@router.post("/{enquiry_id}/reset-overrides", response_model=EnquiryDetailResponse)
async def reset_enquiry_overrides(
    enquiry_id: int,
    session: AsyncSession = Depends(get_session),
) -> EnquiryDetailResponse:
    enquiry = await session.get(Enquiry, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    await enquiries_service.reset_overrides(session, enquiry)
    return await _build_detail(session, enquiry_id)


async def _build_detail(session: AsyncSession, enquiry_id: int) -> EnquiryDetailResponse:
    enquiry, history = await enquiries_service.get_enquiry_detail(session, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    latest_extraction = history[-1] if history else None
    effective_values = resolve_effective_values(enquiry, latest_extraction)
    return build_enquiry_detail_response(enquiry, effective_values, history)
