# Self Review

Three things I'd flag if a senior engineer handed me this code. Short and blunt.

1. **Batch processing is fire-and-forget in-process tasks.** `POST /api/batches` calls
   `asyncio.create_task` and returns; there's no durable job queue, no persistence of
   per-item job state beyond the DB rows, and no resume. Restart the server mid-batch and
   in-flight items are abandoned with the batch stuck at `processing`. For a take-home this
   is defensible, but it's the single weakest part of the system and I would not ship it to a
   real customer without a queue (ARQ/Celery) and idempotent workers.

2. **Effective-value resolution is implicit and spread out.** The "override ?? latest
   extraction" rule lives across `services/effective.py`, `enquiries.py`, `serializers.py`
   and is re-derived in at least three places (list, detail, batch). It has unit tests for
   the pure function but nothing guards the *wiring* — e.g. a new endpoint that returns the
   wrong blend, or a serializer that stops applying overrides, would pass CI. This logic
   should be a single dependency-injected component with contract tests, not a handful of
   hand-synced call sites.

3. **Zero frontend tests.** Backend has 59; the frontend has none — only `tsc` and `oxlint`.
   The inline edit, filters, and re-extract flows are exactly where a regression would hurt a
   human reviewer (typo a key and corrections silently stop persisting), and nothing would
   catch it. Vitest + Testing Library for the table/forms is table stakes before this grows.

Also worth saying: budget normalization is a pile of regexes that has been shaped by the
sample file; it will need a proper parser (or an LLM-in-the-loop for the raw-to-normalized
step) once real enquiries outnumber the 20 in the sample.
