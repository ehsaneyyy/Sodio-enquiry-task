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

NUMBER_WITH_UNIT = r"(\d[\d.,]*)\s*((?:k|thousand|lakh|crore|mn|million|bn|billion|m|b)(?![a-z]))?"
NUMBER_TOKEN = re.compile(NUMBER_WITH_UNIT, re.IGNORECASE)
RANGE_PATTERN = re.compile(
    NUMBER_WITH_UNIT + r"\s*(?:-|–|—|~|\s+to\s+|\s+and\s+|\s+or\s+)\s*[£€₹$]?\s*" + NUMBER_WITH_UNIT,
    re.IGNORECASE,
)
GLOBAL_MAGNITUDE_WORD = re.compile(r"\b(k|thousand|lakh|crore|mn|million|bn|billion|m|b)s?\b", re.IGNORECASE)


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


def _resolve_amount(raw_number: str, suffix: Optional[str], global_multiplier: float) -> float:
    multiplier = MAGNITUDE_MULTIPLIERS.get(suffix.lower(), 1) if suffix else global_multiplier
    return _parse_amount(raw_number, multiplier)


def _global_magnitude_unit(raw: str) -> Optional[str]:
    word_match = GLOBAL_MAGNITUDE_WORD.search(raw)
    if word_match:
        return word_match.group(1).lower()
    for token in NUMBER_TOKEN.finditer(raw):
        if token.group(2):
            return token.group(2).lower()
    return None


def _global_multiplier_from(raw: str) -> float:
    unit = _global_magnitude_unit(raw)
    return MAGNITUDE_MULTIPLIERS.get(unit, 1) if unit else 1


def _single_amount(raw: str, global_multiplier: float) -> Optional[float]:
    tokens = list(NUMBER_TOKEN.finditer(raw))
    if not tokens:
        return None
    symbol_positions = [raw.find(symbol) for symbol in CURRENCY_BY_SYMBOL if raw.find(symbol) != -1]
    if symbol_positions:
        nearest_symbol = min(symbol_positions)
        nearest_token = min(tokens, key=lambda token: abs(token.start() - nearest_symbol))
        return _resolve_amount(nearest_token.group(1), nearest_token.group(2), global_multiplier)
    unit_tokens = [token for token in tokens if token.group(2)]
    target_token = unit_tokens[0] if unit_tokens else tokens[0]
    return _resolve_amount(target_token.group(1), target_token.group(2), global_multiplier)


def parse_budget_string(raw: Optional[str]) -> tuple[Optional[float], Optional[float], Optional[str]]:
    if not raw:
        return None, None, None
    currency = _detect_currency(raw)
    global_multiplier = _global_multiplier_from(raw)
    range_match = RANGE_PATTERN.search(raw)
    if range_match:
        first_amount = _resolve_amount(range_match.group(1), range_match.group(2), global_multiplier)
        second_amount = _resolve_amount(range_match.group(3), range_match.group(4), global_multiplier)
        budget_min, budget_max = min(first_amount, second_amount), max(first_amount, second_amount)
        if currency is None and _global_magnitude_unit(raw) in {"lakh", "crore"}:
            currency = "INR"
        return budget_min, budget_max, currency
    amount = _single_amount(raw, global_multiplier)
    if amount is None:
        return None, None, currency
    if currency is None and _global_magnitude_unit(raw) in {"lakh", "crore"}:
        currency = "INR"
    return amount, amount, currency
