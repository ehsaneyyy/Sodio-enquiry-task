import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.effective import resolve_effective_values
from app.services.enquiries import run_extraction
from app.models import Enquiry
from app.schemas import ExtractionStatus
from app.services.parser import split_enquiries
from app.services.extraction.stub_provider import StubProvider
from app.services.scoring import compute_priority
from app.core.config import get_settings
from app.services.budget import normalize_llm_budget, parse_budget_string

provider = StubProvider()
text = Path("sample-enquiries.txt").read_text(encoding="utf-8")
chunks = split_enquiries(text)
print(f"parsed {len(chunks)} enquiries")
assert len(chunks) == 20, f"expected 20, got {len(chunks)}"

enquiries = [Enquiry(original_text=c, source="file") for c in chunks]

async def main():
    for index, enquiry in enumerate(enquiries, start=1):
        result = await provider.extract(enquiry.original_text)
        budget_min, budget_max, budget_currency = normalize_llm_budget(
            result.budget_min, result.budget_max, result.budget_currency, result.budget_unit
        )
        if budget_min is None and result.budget_raw:
            budget_min, budget_max, budget_currency = parse_budget_string(result.budget_raw)
        enquiry.last_extraction_id = index
        effective = {
            "company": result.company,
            "contact_name": result.contact_name,
            "contact_email": result.contact_email,
            "service_line": result.service_line.value if result.service_line else None,
            "budget_raw": result.budget_raw,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "budget_currency": budget_currency,
            "timeline": result.timeline,
            "timeline_urgency": result.timeline_urgency.value if result.timeline_urgency else None,
            "summary": result.summary,
            "is_genuine": result.is_genuine,
        }
        priority = compute_priority(effective).value
        print(
            f"{index:>2} | {priority:<6} | genuine={str(effective['is_genuine']):<5} | "
            f"svc={effective['service_line'] or '-':<10} | budget={effective['budget_raw'] or '-':<40} "
            f"| norm={budget_min}{'-' + str(budget_max) if budget_max and budget_max != budget_min else ''} "
            f"{budget_currency or ''} | tl={effective['timeline'] or '-'} | "
            f"email={effective['contact_email'] or '-'} | {result.company or '-'}"
        )

asyncio.run(main())
