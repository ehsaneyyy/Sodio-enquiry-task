import pytest

from app.schemas import Priority
from app.services.scoring import compute_priority


def make_effective(**overrides) -> dict:
    effective = {
        "company": None,
        "contact_name": None,
        "contact_email": None,
        "service_line": None,
        "budget_raw": None,
        "budget_min": None,
        "budget_max": None,
        "budget_currency": None,
        "timeline": None,
        "timeline_urgency": None,
        "summary": None,
        "is_genuine": True,
    }
    effective.update(overrides)
    return effective


@pytest.mark.parametrize(
    ("effective", "expected"),
    [
        (make_effective(is_genuine=False, budget_min=100_000), Priority.low),
        (make_effective(is_genuine=True), Priority.low),
        (
            make_effective(
                budget_min=40_000,
                service_line="web",
                contact_name="Rachel",
                contact_email="r@x.co",
                timeline_urgency="near",
            ),
            Priority.high,
        ),
        (
            make_effective(
                budget_raw="around £40,000",
                service_line="ai",
                contact_email="r@x.co",
                timeline_urgency="asap",
            ),
            Priority.high,
        ),
        (make_effective(budget_raw="flexible"), Priority.medium),
        (make_effective(budget_min=1, service_line="web"), Priority.medium),
    ],
)
def test_compute_priority(effective, expected):
    assert compute_priority(effective) == expected


def test_not_genuine_always_low_even_with_budget_and_contacts():
    effective = make_effective(
        is_genuine=False,
        budget_min=1_000_000,
        service_line="blockchain",
        contact_name="A",
        contact_email="a@b.co",
        timeline_urgency="asap",
    )
    assert compute_priority(effective) == Priority.low
