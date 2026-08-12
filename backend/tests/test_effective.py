from app.models import Enquiry, Extraction
from app.schemas import TimelineUrgency
from app.services.effective import (
    infer_urgency_from_timeline,
    list_overridden_fields,
    resolve_effective_values,
)


def test_infer_urgency_asap():
    assert infer_urgency_from_timeline("ASAP — it's down") == TimelineUrgency.asap
    assert infer_urgency_from_timeline("can you start next week") == TimelineUrgency.asap


def test_infer_urgency_flexible():
    assert infer_urgency_from_timeline("Timeline flexible") == TimelineUrgency.flexible
    assert infer_urgency_from_timeline("Budget: TBD") == TimelineUrgency.flexible


def test_infer_urgency_later():
    assert infer_urgency_from_timeline("launching Q1 next year") == TimelineUrgency.later


def test_infer_urgency_near():
    assert infer_urgency_from_timeline("start in September") == TimelineUrgency.near
    assert infer_urgency_from_timeline("within three months") == TimelineUrgency.near


def test_infer_urgency_unknown_and_none():
    assert infer_urgency_from_timeline("some random phrase") == TimelineUrgency.unknown
    assert infer_urgency_from_timeline(None) is None


def test_resolve_effective_values_override_beats_extraction():
    enquiry = Enquiry(original_text="x", company_override="Manual Corp")
    extraction = Extraction(enquiry_id=1, company="Extracted Corp")
    effective = resolve_effective_values(enquiry, extraction)
    assert effective["company"] == "Manual Corp"


def test_resolve_effective_values_falls_back_to_extraction():
    enquiry = Enquiry(original_text="x")
    extraction = Extraction(enquiry_id=1, company="Extracted Corp", timeline_urgency=TimelineUrgency.near)
    effective = resolve_effective_values(enquiry, extraction)
    assert effective["company"] == "Extracted Corp"
    assert effective["timeline_urgency"] == TimelineUrgency.near


def test_resolve_effective_values_derives_urgency_from_timeline_override():
    enquiry = Enquiry(original_text="x", timeline_override="ASAP")
    effective = resolve_effective_values(enquiry, None)
    assert effective["timeline_urgency"] == TimelineUrgency.asap


def test_list_overridden_fields():
    enquiry = Enquiry(original_text="x", budget_min_override=100.0, contact_name_override="A")
    assert set(list_overridden_fields(enquiry)) == {"budget_min", "contact_name"}
