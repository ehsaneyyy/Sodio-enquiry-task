import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_sodio.db"
os.environ["LLM_PROVIDER"] = "stub"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel

from app.core.db import engine
from app.main import app


@pytest.fixture(autouse=True)
async def _fresh_database():
    from app.models import Batch, Enquiry, Extraction

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await connection.run_sync(SQLModel.metadata.create_all)
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


async def wait_for_batch_completion(client: AsyncClient, batch_id: int, timeout: float = 8.0) -> dict:
    deadline = asyncio.get_running_loop().time() + timeout
    last_data: dict = {}
    while asyncio.get_running_loop().time() < deadline:
        response = await client.get(f"/api/batches/{batch_id}")
        last_data = response.json()
        if response.status_code == 200 and last_data.get("status") == "completed":
            return last_data
        await asyncio.sleep(0.05)
    return last_data
