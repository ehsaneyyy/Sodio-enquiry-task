import pytest

GENUINE_TEXT = """From: Rachel Whitfield
Email: r.whitfield@northgate-logistics.co.uk
Message:
Hi, we're a mid-sized logistics firm. We want an internal tool that reads
supplier PDFs automatically. Budget is around £40,000 and we'd start in September.
"""

SPAM_TEXT = """From: Growth Team
Email: outreach@rankfirst-seo.biz
Message:
Guaranteed page-1 rankings starting at $299/month. Reply STOP to unsubscribe.
"""


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_enquiry_runs_extraction(client):
    response = await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})
    assert response.status_code == 201
    data = response.json()
    assert data["extraction_status"] == "success"
    assert data["effective"]["company"] == "Northgate Logistics"
    assert data["effective"]["budget_min"] == 40_000
    assert data["effective"]["budget_currency"] == "GBP"
    assert data["effective"]["is_genuine"] is True
    assert data["priority"] in {"high", "medium", "low"}


async def test_create_enquiry_rejects_empty_text(client):
    response = await client.post("/api/enquiries", json={"original_text": ""})
    assert response.status_code == 422


async def test_list_enquiries_and_filter(client):
    await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})
    await client.post("/api/enquiries", json={"original_text": SPAM_TEXT})

    all_response = await client.get("/api/enquiries")
    assert all_response.status_code == 200
    entries = all_response.json()
    assert len(entries) == 2

    genuine_response = await client.get("/api/enquiries", params={"priority": "high"})
    genuine_entries = genuine_response.json()
    assert all(entry["is_genuine"] for entry in genuine_entries)

    sort_response = await client.get("/api/enquiries", params={"sort": "priority"})
    sorted_entries = sort_response.json()
    assert sorted_entries[0]["priority"] == "high"


async def test_get_enquiry_detail(client):
    created = (await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})).json()
    response = await client.get(f"/api/enquiries/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["latest_extraction"]["company"] == "Northgate Logistics"
    assert len(data["extraction_history"]) == 1


async def test_get_missing_enquiry_returns_404(client):
    response = await client.get("/api/enquiries/9999")
    assert response.status_code == 404


async def test_patch_enquiry_status_and_overrides(client):
    created = (await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})).json()
    response = await client.patch(
        f"/api/enquiries/{created['id']}",
        json={"status": "qualified", "overrides": {"company": "Manual Corp", "budget": "around £60,000"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "qualified"
    assert data["effective"]["company"] == "Manual Corp"
    assert data["effective"]["budget_min"] == 60_000
    assert set(data["overridden_fields"]) == {"company", "budget_raw", "budget_min", "budget_max", "budget_currency"}


async def test_patch_enquiry_unknown_override_field(client):
    created = (await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})).json()
    response = await client.patch(
        f"/api/enquiries/{created['id']}",
        json={"overrides": {"unknown_field": "x"}},
    )
    assert response.status_code == 422


async def test_patch_missing_enquiry_returns_404(client):
    response = await client.patch("/api/enquiries/9999", json={"overrides": {"company": "X"}})
    assert response.status_code == 404


async def test_re_extract_appends_history(client):
    created = (await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})).json()
    response = await client.post(f"/api/enquiries/{created['id']}/re-extract")
    assert response.status_code == 200
    data = response.json()
    assert len(data["extraction_history"]) == 2
    assert data["extraction_status"] == "success"


async def test_reset_overrides_restores_extracted_values(client):
    created = (await client.post("/api/enquiries", json={"original_text": GENUINE_TEXT})).json()
    await client.patch(
        f"/api/enquiries/{created['id']}",
        json={"overrides": {"company": "Manual Corp"}},
    )
    response = await client.post(f"/api/enquiries/{created['id']}/reset-overrides")
    data = response.json()
    assert data["effective"]["company"] == "Northgate Logistics"
    assert data["overridden_fields"] == []
