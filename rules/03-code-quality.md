---
paths:
  - "*/src/*.py"
  - "*/src/**/*.py"
  - "*/main.py"
  - "*/run_*.py"
  - "*/tests/**/*.py"
---

# Phase 2 — Code Quality

> Phase 1 → [`02-code-layout.md`](02-code-layout.md) | Next → [`04-error-and-logging.md`](04-error-and-logging.md)
> Repository + prompt specifics → [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py)
> **Scope:** per-function quality — how each function is written. File / layer / placement decisions live in [`02-code-layout.md`](02-code-layout.md) and are NOT restated here.

## SECTION 1: FUNCTION SIZE & SPLITTING

> Why 25 lines, and why *not* fewer: 25 lines is one screen — a reviewer holds the whole function in their head at once. The limit is a ceiling, not a target. Splitting below it trades one readable unit for a call chain the reader must reassemble, which is the more common failure here.

- Every function MUST be **≤ 25 lines**.
- **A multi-line literal counts as one line.** The 25-line limit measures statements, not physical lines — a 24-key dict written one key per line (Section 2) is one statement and must not force a split that has no other reason.
- Split into helpers ONLY when a function exceeds 25 lines. Below it, consolidate: 4×5-line functions that belong together are one 25-line function, and a tiny helper called from one place is inlined.
- **Exception:** sub-functions keeping `run_*` free of business logic are justified even if single-use.

## SECTION 2: FORMATTING

> Why a width cap: a line you have to scroll three screens to read is a line nobody reviews. The old "never break a line" rule optimised for `git diff` and paid for it in unreadable 600-character statements. 160 columns fits a split editor pane.

- **Maximum line width: 150–160 characters.** Hard cap. A statement over it MUST be broken.
- Function signatures on a **single line** — no splitting parameters.
- Statements that fit stay on one line — no gratuitous wrapping.
- **Long dict / list / object literals are written multi-line**, one key per line, keys aligned under the first key, closing brace on the last line. No trailing hanging indent, no scrolling right.
- **No nested calls.** A call whose argument is another service or repository call gets split into two statements with a named intermediate. `x.get(KEY)` accessors stay inline.
- No comment-based headers (`# --- Step 1 ---`) inside functions.

```python
batch_context = {"run_id": task_data["run_id"],
                 "file_contexts": file_contexts,
                 "statement_lines_count": statement_lines_count,
                 "consumed_email_row_ids": set()}
```

## SECTION 3: VARIABLE HYGIENE

> Why names carry the weight: with no type hints and no comments (Section 5), the variable name is the only documentation the next reader gets. A single-use intermediate adds a name to track without adding information.

- Every variable name conveys what it holds and why it exists — no single-letter names (`i`, `r`, `e`, `x`).
- Variables declared **close to first use** — not top-of-function blocks.
- No `current_step` tracking variables — stack trace provides failure location.
- A variable is justified when it is used **more than once**, feeds a conditional, **or brings a statement under the 160-character cap or un-nests a call** (Section 2) — width and nesting win. Otherwise inline the value directly in the call.

## SECTION 4: CONTROL FLOW

> Why happy path only: this service runs in a controlled environment with fixed, known inputs, and Phase 3's single try/except already catches anything unexpected and logs it to Splunk. A defensive check for a case that cannot occur is untestable, untested code that hides the real failure instead of surfacing it.

- No single-line loops or list comprehensions used as statements.
- All `for`/`while` in standard multi-line block format.
- List comprehensions OK only for simple transformations; prefer loops if complex.
- Assume all inputs/outputs are valid. No defensive edge-case code. Happy path only — unexpected failure → top-level try/except (Phase 3) catches it.
- The runtime environment is controlled: file names and structure are fixed and known. Code ONLY for the fixed inputs — never handle cases that cannot occur, never generalize beyond them.

## SECTION 5: MINIMAL CODE

> Why no comments, docstrings, or type hints: the whole codebase follows one shape — `task_data`/`flow_id` through every layer, one file per feature, one try/except per function. Names carry the intent, and annotations or comments that restate a signature go stale silently and start lying to the next reader. Every line here is a line someone maintains.

- Write ONLY what is strictly necessary. Every line must justify its existence.
- No premature abstractions (need 2+ use cases). No boilerplate / scaffolding / stubs.
- No comments, no docstrings, no type hints or annotations — not on signatures, parameters, return values or variables (no `: str`, `: dict`, `-> None`, `-> list[...]`). Plain Python only; clear naming conveys intent.
- **Three exceptions, and no others.** Pydantic `BaseModel` field declarations, which Pydantic requires. FastAPI route-signature annotations, where the framework requires them. The input/output header comment at the top of a GPT repository file. This list is closed and lives only here — no directory rule adds to it or claims one of these as its own.
- No unused return values — if no caller reads the result, use a bare `return` (no value).
- No trivial wrappers: if a function only constructs args (**1–3 lines**) and delegates → inline at call site. **4+ lines** of construction justify a dedicated method. This is the threshold every layer uses, including a CRM payload. Wrappers are also justified by complex logic (loops, conditionals, multi-step). If a shared method already logs STARTING/FINISHED/ERROR → wrappers MUST NOT add duplicate logs.

## SECTION 6: DATA SAFETY

> Why: a `DELETE` + `INSERT` pair that fails between the two statements leaves the table short of rows that existed before the run. MERGE/UPSERT makes a re-run harmless.

- Never `DELETE` + `INSERT` for idempotent writes — use MERGE/UPSERT or check-then-insert.

## SECTION 7: NO UNEARNED COMPLEXITY

> Why: complexity is paid for once when it is written and forever when it is read, debugged and changed. A mechanism that does not solve a problem this service actually has is not neutral — it is a permanent cost with no return, and it hides the failures that matter behind failures that do not.

- **The simple version is the default.** A more complex mechanism is chosen only when the simple one has been shown to be insufficient — not because it might be later, and not because it is the more interesting solution.
- **Every mechanism justifies itself against a real constraint of this service.** Name the constraint. "It could be slow" is not one; a measured limit is.
- **Complexity is not free at any layer** — concurrency, caching, retries, abstraction layers, configuration switches, generalised helpers. All of it obeys the same test.
- **Example — concurrency.** Parallelism is never the first choice. It earns its place in a synchronous service that must answer fast, where latency is the constraint. In a cron job that runs alone and unattended it buys nothing worth having: it complicates failure handling, makes the logs interleave, and pushes load at rate-limited external services for no deadline anyone is waiting on. Sequential unless there is a stated reason.
- **A removed mechanism does not come back without a reason.** If a simplification is deliberate, it is written down under the shared root's `docs/spec/` so the next reader does not "fix" it back.

## REVIEW CHECKLIST
- [ ] Every function ≤ 25 statements, multi-line literals counted as one (Section 1)
- [ ] Minimum functions — no unnecessary splitting (Section 1)
- [ ] No line over 160 characters (Section 2)
- [ ] Long literals multi-line, keys aligned; no nested service/repository calls (Section 2)
- [ ] Function signatures on a single line (Section 2)
- [ ] No comment-header banners inside functions (Section 2)
- [ ] All variables have descriptive, meaningful names — no single-letter (Section 3)
- [ ] Variables close to first use, no single-use intermediates except for width / un-nesting, no `current_step` (Section 3)
- [ ] Loops in multi-line form; comprehensions only for trivial transforms (Section 4)
- [ ] No edge-case / defensive checks (Section 4)
- [ ] Code targets only the fixed, known inputs — no handling of impossible cases, no generalization (Section 4)
- [ ] No comments / docstrings / type hints outside the three exceptions in Section 5
- [ ] No unused return values — bare `return` if discarded (Section 5)
- [ ] No trivial wrappers (1–3 lines of arg construction → inline), no redundant logging (Section 5)
- [ ] No `DELETE` + `INSERT` for idempotent writes (Section 6)
- [ ] Every mechanism answers a stated constraint of this service — no unearned complexity (Section 7)
- [ ] Sequential unless a named latency constraint says otherwise (Section 7)
- [ ] Phase 1 layout rules already enforced — file placement, layer contracts, `task_data` / `flow_id` flow (see [`02-code-layout.md`](02-code-layout.md))
