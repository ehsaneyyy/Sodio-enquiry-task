import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.parser import split_enquiries
from app.services.extraction.stub_provider import StubProvider

chunks = split_enquiries(Path("sample-enquiries.txt").read_text(encoding="utf-8"))
fifth = chunks[4]
print("=== chunk 5 raw ===")
print(repr(fifth[:300]))
print("=== message ===")
message = StubProvider._extract_message(fifth)
print(repr(message[:300]))
print("contains 'aplicación móvil':", "aplicación móvil" in message.lower())
print("contains 'móvil':", "móvil" in message.lower())

async def run():
    result = await StubProvider().extract(fifth)
    print("service:", result.service_line)
    print("budget_raw:", result.budget_raw)
    print("budget_min/max/cur:", result.budget_min, result.budget_max, result.budget_currency)

asyncio.run(run())
