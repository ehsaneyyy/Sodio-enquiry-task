import asyncio

import pytest

from tests.conftest import wait_for_batch_completion

SEPARATOR = "-" * 80

BATCH_FILE = f"""From: Rachel Whitfield
Email: r.whitfield@northgate-logistics.co.uk
Message:
Need an internal tool for supplier PDFs. Budget around £40,000, start in September.
{SEPARATOR}
From: Growth Team
Email: outreach@rankfirst-seo.biz
Message:
Guaranteed page-1 rankings starting at $299/month. Reply STOP to unsubscribe.
{SEPARATOR}
From: D. Fontaine
Email: fontaine@luckystar-gaming.cw
Message:
Want crypto deposits and a provably fair dice game. Budget $80k. Start next week?
"""


async def test_upload_batch_and_process(client):
    response = await client.post(
        "/api/batches",
        files={"file": ("enquiries.txt", BATCH_FILE.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["total"] == 3
    assert len(payload["enquiry_ids"]) == 3

    detail = await wait_for_batch_completion(client, payload["batch_id"])
    assert detail["completed_count"] == 3
    assert detail["failed_count"] == 0
    assert detail["status"] == "completed"
    assert all(item["extraction_status"] == "success" for item in detail["items"])


async def test_upload_empty_file_rejected(client):
    response = await client.post("/api/batches", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 422


async def test_get_missing_batch_returns_404(client):
    response = await client.get("/api/batches/9999")
    assert response.status_code == 404


async def test_retry_failed_batch(client):
    created = (
        await client.post(
            "/api/batches",
            files={"file": ("enquiries.txt", BATCH_FILE.encode("utf-8"), "text/plain")},
        )
    ).json()
    await wait_for_batch_completion(client, created["batch_id"])

    response = await client.post(f"/api/batches/{created['batch_id']}/retry-failed")
    assert response.status_code == 202
    assert response.json()["total"] == 0
