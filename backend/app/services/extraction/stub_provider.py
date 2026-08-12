import re
from typing import Optional

from app.schemas import ExtractionResult, ServiceLine
from app.services.budget import parse_budget_string
from app.services.effective import infer_urgency_from_timeline
from app.services.extraction.interface import LLMProvider

GENERIC_SENDER_LABELS = {
    "website contact form",
    "system",
    "admin",
    "unknown",
    "operations",
    "growth team",
    "talent acquisition",
}

TOP_LEVEL_DOMAINS = {
    "com", "co", "org", "net", "edu", "io", "uk", "de", "es", "jp", "in", "cw", "xyz", "biz", "dev", "app",
}

SERVICE_KEYWORD_ORDER = [
    (ServiceLine.game, ["game", "gaming", "casino", "dice"]),
    (ServiceLine.blockchain, ["token", "smart contract", "blockchain", "escrow", "crypto", "staking", "defi", "nft"]),
    (ServiceLine.ai, ["chatbot", "ai model", "ai thing", "ai agents", "ai agent", "fine-tun", "machine learning", "demand forecasting", "automatically"]),
    (ServiceLine.mobile, ["mobile app", "aplicación móvil", "app for", "ios", "android"]),
    (ServiceLine.web, ["website", "landing page", "portal", "dashboard", "web app", "react admin", "backend", "node app", "internal tool", "platform"]),
]

FROM_LINE = re.compile(r"^From:\s*(.+?)\s*$", re.MULTILINE)
EMAIL_LINE = re.compile(r"^Email:\s*(.+?)\s*$", re.MULTILINE)
NAME_IN_BODY = re.compile(r"^Name:\s*(.+?)\s*$", re.MULTILINE)
MESSAGE_LINE = re.compile(r"^Message:\s*(.*)$", re.MULTILINE)
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
AMOUNT_LINE = re.compile(r"[£€₹$]|\d[\d.,]*\s*[kKmMbB]\b|lakh|crore", re.IGNORECASE)
BUDGET_KEYWORD_LINE = re.compile(r"budget|allocated|allocation|spend|costs|presupuesto|pay|tbd|flexible|charge", re.IGNORECASE)
TIMELINE_PATTERNS = [
    (r"\basap\b", "ASAP"),
    (r"next week", "next week"),
    (r"6 weeks", "6 weeks"),
    (r"start in september", "start in September"),
    (r"before diwali", "before Diwali"),
    (r"three months", "three months"),
    (r"q1 next year", "Q1 next year"),
    (r"eighteen months", "eighteen months"),
    (r"timeline flexible", "Timeline flexible"),
    (r"budget:?\s*tbd", "TBD"),
    (r"flexible", "flexible"),
]


class StubProvider(LLMProvider):
    name = "stub/heuristic"

    async def extract(self, enquiry_text: str) -> ExtractionResult:
        from_line = self._first_match(FROM_LINE, enquiry_text)
        email_line = self._first_match(EMAIL_LINE, enquiry_text)
        sender = from_line or None
        email = self._clean_email(email_line)
        message = self._extract_message(enquiry_text)

        return ExtractionResult(
            company=self._guess_company(sender, email, enquiry_text),
            contact_name=self._guess_contact_name(sender, enquiry_text),
            contact_email=email,
            service_line=self._guess_service_line(message),
            budget_raw=self._guess_budget_raw(message),
            budget_min=self._parsed_budget(message)[0],
            budget_max=self._parsed_budget(message)[1],
            budget_currency=self._parsed_budget(message)[2],
            timeline=self._guess_timeline(message),
            timeline_urgency=self._guess_timeline_urgency(message),
            summary=self._make_summary(message),
            is_genuine=self._is_genuine(sender, email, message),
        )

    @staticmethod
    def _first_match(pattern: re.Pattern[str], text: str) -> Optional[str]:
        match = pattern.search(text)
        return match.group(1).strip() if match else None

    @staticmethod
    def _clean_email(raw_email: Optional[str]) -> Optional[str]:
        if raw_email and EMAIL_PATTERN.match(raw_email.strip()):
            return raw_email.strip()
        return None

    @staticmethod
    def _extract_message(text: str) -> str:
        positions = [match.start() for match in MESSAGE_LINE.finditer(text)]
        if not positions:
            return text.strip()
        message = text[positions[-1]:]
        message = re.sub(r"^Message:\s*", "", message, count=1)
        return message.strip()

    @staticmethod
    def _guess_company(sender: Optional[str], email: Optional[str], text: str) -> Optional[str]:
        domain = email.split("@")[-1] if email else None
        if domain:
            parts = [part.capitalize() for part in re.split(r"[\W_]+", domain) if part and part.lower() not in TOP_LEVEL_DOMAINS]
            if parts:
                return " ".join(parts)
        if sender and sender.lower() not in GENERIC_SENDER_LABELS:
            return sender
        return None

    @staticmethod
    def _guess_contact_name(sender: Optional[str], text: str) -> Optional[str]:
        if sender and sender.lower() not in GENERIC_SENDER_LABELS:
            return sender
        name = StubProvider._first_match(NAME_IN_BODY, text)
        if name:
            return name
        return None

    @staticmethod
    def _guess_service_line(message: str) -> ServiceLine:
        normalized = message.lower()
        for service_line, keywords in SERVICE_KEYWORD_ORDER:
            for keyword in keywords:
                if keyword in normalized:
                    return service_line
        return ServiceLine.other

    @staticmethod
    def _guess_budget_raw(message: str) -> Optional[str]:
        for line in message.splitlines():
            stripped = line.strip()
            if AMOUNT_LINE.search(stripped):
                return stripped[:200]
        for line in message.splitlines():
            stripped = line.strip()
            if BUDGET_KEYWORD_LINE.search(stripped):
                return stripped[:200]
        return None

    @staticmethod
    def _parsed_budget(message: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
        raw = StubProvider._guess_budget_raw(message)
        return parse_budget_string(raw)

    @staticmethod
    def _guess_timeline(message: str) -> Optional[str]:
        normalized = message.lower()
        for pattern, label in TIMELINE_PATTERNS:
            if re.search(pattern, normalized):
                return label
        return None

    @staticmethod
    def _guess_timeline_urgency(message: str) -> Optional[str]:
        timeline = StubProvider._guess_timeline(message)
        urgency = infer_urgency_from_timeline(timeline)
        return urgency.value if urgency else None

    @staticmethod
    def _make_summary(message: str) -> Optional[str]:
        collapsed = re.sub(r"\s+", " ", message).strip()
        if not collapsed:
            return None
        return collapsed[:200]

    @staticmethod
    def _is_genuine(sender: Optional[str], email: Optional[str], message: str) -> bool:
        lowered = message.lower()
        sender_label = sender.lower() if sender else ""
        if "ignore all previous instructions" in lowered:
            return False
        if sender_label in {"system", "admin", "unknown"}:
            return False
        if "delivery status notification" in lowered or "bounce" in lowered:
            return False
        if re.search(r"unsubscribe|guaranteed page-1|seo|rank.*keyword", lowered):
            return False
        if re.search(r"recruit|place.*engineer|hiring needs|15-minute call", lowered):
            return False
        if re.search(r"capstone|no budget|experience for me|final-year", lowered):
            return False
        if len(message) < 20:
            return False
        return True
