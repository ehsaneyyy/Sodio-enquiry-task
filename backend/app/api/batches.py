import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_llm_provider
from app.core.db import get_session
from app.models import Batch, Enquiry
from app.schemas import BatchCreatedResponse, BatchDetailResponse, BatchItemResponse
from app.services import batches as batches_service
from app.services.extraction.interface import LLMProvider
from app.services.parser import read_enquiry_file

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("", status_code=202, response_model=BatchCreatedResponse)
async def create_enquiry_batch(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    provider: LLMProvider = Depends(get_llm_provider),
) -> BatchCreatedResponse:
    content = await file.read()
    enquiries_text = read_enquiry_file(content)
    if not enquiries_text:
        raise HTTPException(status_code=422, detail="No enquiries found in the uploaded file")
    batch = Batch(filename=file.filename, status="processing", total=len(enquiries_text))
    session.add(batch)
    await session.flush()
    enquiry_ids: list[int] = []
    for text in enquiries_text:
        enquiry = Enquiry(original_text=text, source="file", batch_id=batch.id, extraction_status="pending")
        session.add(enquiry)
        await session.flush()
        enquiry_ids.append(enquiry.id)
    await session.commit()
    asyncio.create_task(batches_service.process_batch(batch.id, provider))
    return BatchCreatedResponse(batch_id=batch.id, enquiry_ids=enquiry_ids, total=len(enquiries_text))


@router.get("/{batch_id}", response_model=BatchDetailResponse)
async def get_batch_detail(
    batch_id: int,
    session: AsyncSession = Depends(get_session),
) -> BatchDetailResponse:
    batch = await session.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    enquiries = list((await session.exec(select(Enquiry).where(Enquiry.batch_id == batch_id))).all())
    counts = {"success": 0, "failed": 0, "pending": 0, "processing": 0}
    items: list[BatchItemResponse] = []
    for enquiry in enquiries:
        counts[enquiry.extraction_status] = counts.get(enquiry.extraction_status, 0) + 1
        items.append(
            BatchItemResponse(enquiry_id=enquiry.id, extraction_status=enquiry.extraction_status, error=enquiry.extraction_error)
        )
    return BatchDetailResponse(
        id=batch.id,
        filename=batch.filename,
        status=batch.status,
        total=batch.total,
        completed_count=counts["success"],
        failed_count=counts["failed"],
        pending_count=counts["pending"],
        processing_count=counts["processing"],
        items=items,
    )


@router.post("/{batch_id}/retry-failed", status_code=202, response_model=BatchCreatedResponse)
async def retry_failed_batch_items(
    batch_id: int,
    session: AsyncSession = Depends(get_session),
    provider: LLMProvider = Depends(get_llm_provider),
) -> BatchCreatedResponse:
    batch = await session.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    failed_ids = await batches_service.collect_failed_enquiry_ids(session, batch_id)
    batch.status = "processing"
    await session.commit()
    asyncio.create_task(batches_service.process_batch(batch_id, provider, failed_ids))
    return BatchCreatedResponse(batch_id=batch_id, enquiry_ids=failed_ids, total=len(failed_ids))
