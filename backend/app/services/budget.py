import re
from typing import Optional

from app.schemas import BudgetUnit

MAGNITUDE_MULTIPLIERS = {
    "k": 1_000,
    "thousand": 1_000,
    "lakh": 100_000,
    "crore": 10_000_000,
    "mn": 1_000_000,
    "m": 1_000_000,
    "million": 1_000_000,
    "bn": 1_000_000_000,
    "b": 1_000_000_000,
    "billion": 1_000_000_000,
}

CURRENCY_BY_SYMBOL = {"£": "GBP", "€": "EUR", "$": "USD", "₹": "INR"}

CURRENCY_BY_WORD = {
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "eur": "EUR",
    "euro": "EUR",
    "euros": "EUR",
    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
}

NUMBER_TOKEN = re.compile(r"(\d[\d.,]*)\s*((?:k|thousand|lakh|crore|mn|million|bn|billion|m|b)(?![a-z]))?", re.IGNORECASE)
GLOBAL_MAGNITUDE_WORD = re.compile(r"\b(k|thousand|lakh|crore|mn|million|bn|billion|m|b)\b", re.IGNORECASE)
RANGE_CONNECTOR = re.compile(r"-|–|—|~|\s+to\s+|\sand\s|\sor\s", re.IGNORECASE)


def normalize_llm_budget(
    amount_min: Optional[float],
    amount_max: Optional[float],
    currency: Optional[str],
    unit: BudgetUnit,
) -> tuple[Optional[float], Optional[float], Optional[str]]:
    multiplier = MAGNITUDE_MULTIPLIERS.get(unit.value, 1)
    normalized_min = amount_min * multiplier if amount_min is not None else None
    normalized_max = amount_max * multiplier if amount_max is not None else None
    if normalized_min is not None and normalized_max is not None and normalized_min > normalized_max:
        normalized_min, normalized_max = normalized_max, normalized_min
    return normalized_min, normalized_max, currency


def _detect_currency(raw: str) -> Optional[str]:
    normalized = raw.lower()
    for symbol, code in CURRENCY_BY_SYMBOL.items():
        if symbol in raw:
            return code
    for word, code in CURRENCY_BY_WORD.items():
        if re.search(rf"\b{word}\b", normalized):
            return code
    return None


def _parse_amount(raw_number: str, multiplier: float) -> float:
    if "," in raw_number:
        raw_number = raw_number.replace(",", "")
    elif "." in raw_number:
        integer_part, _, fraction_part = raw_number.partition(".")
        if len(fraction_part) == 3:
            raw_number = raw_number.replace(".", "")
    return float(raw_number) * multiplier


def parse_budget_string(raw: Optional[str]) -> tuple[Optional[float], Optional[float], Optional[str]]:
    if not raw:
        return None, None, None
    currency = _detect_currency(raw)
    global_match = GLOBAL_MAGNITUDE_WORD.search(raw)
    global_multiplier = MAGNITUDE_MULTIPLIERS.get(global_match.group(1).lower(), 1) if global_match else 1
    amounts: list[float] = []
    for match in NUMBER_TOKEN.finditer(raw):
        suffix_multiplier = MAGNITUDE_MULTIPLIERS.get(match.group(2).lower(), 1) if match.group(2) else global_multiplier
        amounts.append(_parse_amount(match.group(1), suffix_multiplier))
    if not amounts:
        return None, None, currency
    if len(amounts) == 1:
        return amounts[0], amounts[0], currency
    if RANGE_CONNECTOR.search(raw):
        return min(amounts[0], amounts[1]), max(amounts[0], amounts[1]), currency
    return amounts[0], amounts[0], currency
