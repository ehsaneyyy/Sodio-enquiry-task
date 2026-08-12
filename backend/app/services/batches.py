import asyncio
from typing import Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.db import session_factory
from app.models import Batch, Enquiry
from app.services.enquiries import run_extraction
from app.services.extraction.interface import LLMProvider


async def process_enquiry_ids(enquiry_ids: list[int], provider: LLMProvider) -> None:
    semaphore = asyncio.Semaphore(get_settings().batch_concurrency)

    async def worker(enquiry_id: int) -> None:
        async with semaphore:
            try:
                async with session_factory() as session:
                    enquiry = await session.get(Enquiry, enquiry_id)
                    if enquiry is None:
                        return
                    await run_extraction(
                        session,
                        enquiry,
                        provider,
                        provider.name,
                        get_settings().extraction_prompt_version,
                    )
            except Exception:
                try:
                    async with session_factory() as session:
                        enquiry = await session.get(Enquiry, enquiry_id)
                        if enquiry is not None:
                            enquiry.extraction_status = "failed"
                            enquiry.extraction_error = "Unexpected batch processing error"
                            await session.commit()
                except Exception:
                    pass

    await asyncio.gather(*(worker(enquiry_id) for enquiry_id in enquiry_ids))


async def process_batch(batch_id: int, provider: LLMProvider, enquiry_ids: Optional[list[int]] = None) -> None:
    resolved_ids = enquiry_ids
    if resolved_ids is None:
        async with session_factory() as session:
            enquiries = list((await session.exec(select(Enquiry).where(Enquiry.batch_id == batch_id))).all())
            resolved_ids = [enquiry.id for enquiry in enquiries]
    await process_enquiry_ids(resolved_ids, provider)
    async with session_factory() as session:
        batch = await session.get(Batch, batch_id)
        if batch is not None:
            batch.status = "completed"
            await session.commit()


async def collect_failed_enquiry_ids(session: AsyncSession, batch_id: int) -> list[int]:
    enquiries = list(
        (
            await session.exec(
                select(Enquiry).where(Enquiry.batch_id == batch_id, Enquiry.extraction_status == "failed")
            )
        ).all()
    )
    return [enquiry.id for enquiry in enquiries]
