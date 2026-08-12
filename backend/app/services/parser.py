import re
from typing import Optional

SEPARATOR_LINE = re.compile(r"^-{40,}\s*$", re.MULTILINE)
PREAMBLE_MARKERS = ["sample", "test data", "instructions", "do not edit", "separated by", "dashes", "enquiries task"]


def looks_like_preamble(chunk: str) -> bool:
    normalized = chunk.lower()
    if re.search(r"^from:\s", normalized, re.MULTILINE):
        return False
    if re.search(r"^message:\s", normalized, re.MULTILINE):
        return False
    return any(marker in normalized for marker in PREAMBLE_MARKERS)


def split_enquiries(text: str) -> list[str]:
    chunks = re.split(SEPARATOR_LINE, text)
    enquiries: list[str] = []
    for chunk in chunks:
        stripped = chunk.strip()
        if not stripped:
            continue
        if not enquiries and looks_like_preamble(stripped):
            continue
        enquiries.append(stripped)
    return enquiries


def read_enquiry_file(content: bytes) -> list[str]:
    text = content.decode("utf-8", errors="replace")
    return split_enquiries(text)
