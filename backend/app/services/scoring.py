from typing import Any

from app.schemas import Priority

GENUINE_PROJECT_POINTS = 4
BUDGET_AMOUNT_POINTS = 2
BUDGET_MENTIONED_POINTS = 1
TIMELINE_ASAP_POINTS = 2
TIMELINE_NEAR_POINTS = 1
RECOGNIZED_SERVICE_POINTS = 1
FULL_CONTACT_POINTS = 2
PARTIAL_CONTACT_POINTS = 1
HIGH_THRESHOLD = 9
MEDIUM_THRESHOLD = 5


def compute_priority(effective_values: dict[str, Any]) -> Priority:
    if effective_values.get("is_genuine") is not True:
        return Priority.low
    score = GENUINE_PROJECT_POINTS
    if effective_values.get("budget_min") is not None or effective_values.get("budget_max") is not None:
        score += BUDGET_AMOUNT_POINTS
    elif effective_values.get("budget_raw"):
        score += BUDGET_MENTIONED_POINTS
    urgency = effective_values.get("timeline_urgency")
    if urgency == "asap":
        score += TIMELINE_ASAP_POINTS
    elif urgency == "near":
        score += TIMELINE_NEAR_POINTS
    service_line = effective_values.get("service_line")
    if service_line and service_line != "other":
        score += RECOGNIZED_SERVICE_POINTS
    contact_name = effective_values.get("contact_name")
    contact_email = effective_values.get("contact_email")
    if contact_name and contact_email:
        score += FULL_CONTACT_POINTS
    elif contact_name or contact_email:
        score += PARTIAL_CONTACT_POINTS
    if score >= HIGH_THRESHOLD:
        return Priority.high
    if score >= MEDIUM_THRESHOLD:
        return Priority.medium
    return Priority.low
