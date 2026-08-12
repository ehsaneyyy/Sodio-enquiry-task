# AI Log

## Tools used

- **OpenCode (CLI coding agent)** — primary implementation tool for both backend and frontend.
- **ChatGPT** — used *before* coding to pressure-test my reading of the brief and shape the
  architecture (stack choice, override-based re-extraction model, batch concurrency approach).
  That guidance is archived locally in `TASK-BRIEF.md` (gitignored, not part of the submission).
- **pytest / tsc / oxlint / git / Node** — verification and debugging around the agent.

## Concrete moments the model got it wrong

### 1. Overlapping edits corrupted a file the agent had just written

While building the enquiry detail page, an edit was applied on top of the file it had just
written and produced duplicated declarations — `company: string` twice, a duplicated
`const effective = ...`, and `ServiceLine | "unset" | "unset"`.

**What I noticed:** `tsc -b` failed with `TS2403: Subsequent variable declarations must have
the same type` at a spot that looked unrelated to the JSX (it was the cascade landing on a
closing tag). The line-number-1-based read of the file and a raw byte dump disagreed, which is
what tipped me off that the file on disk was structurally corrupt rather than there being a
real logic bug.

**What I did:** rewrote the corrupted blocks by hand (`interface OverrideFormState` and
`initialFormState`), re-read the exact lines, then re-ran the typecheck. Lesson: after any
multi-part edit, re-read the target region before trusting a successful write.

### 2. JSX TypeScript's parser rejected — and the error was not where the bug was

The agent wrote an extraction-history panel with a conditional in JSX children shaped like:

```
{cond ? ( <p/> ) : ( <dl>…</dl> {summary ? ( <p/> ) : null} )}
```

i.e. a ternary else-branch with two sibling children, the second being another expression
container. `tsc` reported `')' expected` at line 171, column 15 and a cascade of
"Expected corresponding JSX closing tag" errors — none of which pointed at the real structure.

**What I noticed:** the source looked balanced by eye. I wrote a character-level bracket
balancer and then binary-searched minimal reproductions with `transpileModule`, which isolated
the failing pattern to exactly this construct. That proved it wasn't my reading of the file —
it's a TypeScript parser limitation around a ternary else-branch whose second sibling is a JSX
expression container.

**What I did:** rewrote the construct to wrap the else-branch in a fragment (`<>…</>`), which
parses cleanly and adds no DOM node. The full build then passed.

### 3. Async test suite hung / "database is locked" — cross-test pollution

Batch upload spawns a fire-and-forget `asyncio.create_task` for processing, and the test DB
used a module-level async engine with connection pooling. Running the batch API tests followed
by the service tests produced `sqlite3.OperationalError: database is locked` in tests that
don't touch batches at all, and the suite ballooned to ~96 s.

**What I noticed:** the whole suite hung for 3+ minutes on the first full run, then a subset
run showed 15 of the errors were all "database is locked" — all in tests that merely drop/recreate
tables at setup. Isolation (running files alone passed) pointed at state leaking between
tests: leftover background tasks plus pooled aiosqlite connections bound to a closed event loop.

**What I did:** (a) an autouse fixture that cancels lingering tasks and disposes the engine
after every test; (b) `NullPool` for SQLite so no connection is ever reused across loops.
Result: full suite green and stable, 59 passed in ~6 s instead of hanging.

## General notes

The agent was consistently strong on conventions (zero-comment code policy, feature-based
React structure, Clean-Architecture layering in FastAPI) — the failures above were all about
trusting the previous state of files and the toolchain's assumptions, which is exactly where
the human had to step in and verify.
