import pytest

from app.schemas import BudgetUnit
from app.services.budget import normalize_llm_budget, parse_budget_string


@pytest.mark.parametrize(
    ("raw", "expected_min", "expected_max", "expected_currency"),
    [
        ("Budget is around £40,000", 40_000, 40_000, "GBP"),
        ("Presupuesto aproximado 25.000 €", 25_000, 25_000, "EUR"),
        ("guaranteed page-1 rankings starting at $299/month", 299, 299, "USD"),
        ("somewhere between $60k and $90k", 60_000, 90_000, "USD"),
        ("Budget $80k", 80_000, 80_000, "USD"),
        ("Need a data pipeline and dashboard. 20-30k.", 20_000, 30_000, None),
        ("Roughly 35-40 lakhs allocated", 3_500_000, 4_000_000, "INR"),
        ("10000000 USD", 10_000_000, 10_000_000, "USD"),
        ("flexible", None, None, None),
        ("I don't have any budget", None, None, None),
        ("", None, None, None),
        (None, None, None, None),
    ],
)
def test_parse_budget_string(raw, expected_min, expected_max, expected_currency):
    assert parse_budget_string(raw) == (expected_min, expected_max, expected_currency)


@pytest.mark.parametrize(
    ("amount_min", "amount_max", "currency", "unit", "expected"),
    [
        (50, None, "USD", BudgetUnit.base, (50, None, "USD")),
        (50, None, "USD", BudgetUnit.thousand, (50_000, None, "USD")),
        (2, 3, None, BudgetUnit.lakh, (200_000, 300_000, None)),
        (3, 2, "GBP", BudgetUnit.base, (2, 3, "GBP")),
        (None, None, None, BudgetUnit.base, (None, None, None)),
        (None, 5, "EUR", BudgetUnit.million, (None, 5_000_000, "EUR")),
    ],
)
def test_normalize_llm_budget(amount_min, amount_max, currency, unit, expected):
    assert normalize_llm_budget(amount_min, amount_max, currency, unit) == expected
