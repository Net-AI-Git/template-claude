---
paths:
  - "*/src/*.py"
  - "*/src/**/*.py"
  - "*/main.py"
  - "*/run_*.py"
---

# Phase 1 — Code Layout

> Phase 0 → [`01-teach-lesson.md`](01-teach-lesson.md) | Next → [`03-code-quality.md`](03-code-quality.md) → [`04-error-and-logging.md`](04-error-and-logging.md)
> Repository + prompt specifics → [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py)
> **Scope:** *where* code lives — files, directories, layers, placement, layer contracts. Per-function quality (size, formatting, variables, minimalism, data safety) lives in [`03-code-quality.md`](03-code-quality.md).

## SECTION 1: FILE & DIRECTORY STRUCTURE — FLAT, NOT NESTED

> Why flat: a feature's blast radius must be readable from the file tree alone. One predictable path per artifact means a reviewer finds any feature without searching, and deleting a feature touches a known, finite set of files.

- Services: `services/<feature_name>_service.py` — one file per feature, directly in `services/`. Module-level functions, no class. The entry point is `run_<feature_name>(task_data, flow_id)`; a **flow function** that orchestrates several services rather than belonging to one is named `<flow_name>_flow`.
- **One scope per file.** A file may hold more than one function — or, in `repositories/`, more than one class — when they belong to the same scope and are read together. Splitting a scope across files to satisfy a count makes the reader open three files to follow one flow — that is worse than the thing it avoids. Two things that are not read together belong in two files.
- GPT repos: `repositories/gpt_<feature_name>_repository.py` — one file per feature.
- Oracle DB: all features share `repositories/oracle_repository.py` (methods added to same class).
- CRM: all features share `repositories/crm_repository.py`.
- Shared infra: `redis_repository.py`, `splunk_repository.py` in `repositories/`.
- Pydantic schemas: every `BaseModel` lives under `schemas/` — never beside the code that uses it, never inside a repository, service or route. How that directory splits into files is [`14-schemas.md`](14-schemas.md).
- Do NOT create subdirectories per feature. Feature files are self-contained — all logic stays in its own file(s).
- New feature scope: new service file + new GPT repo file (if LLM) + new response model class in `schemas/gpt_responses.py` (if LLM) + new methods in oracle/crm repos (if needed) + one call in orchestrator. NO other files modified.

## SECTION 2: NAMING CONVENTIONS

> Why names must be self-explaining: this codebase carries no comments, docstrings, or type hints ([`03-code-quality.md`](03-code-quality.md) Section 5), so the name is the only thing telling the next reader what an artifact does. `feature_10` forces a hunt through Jira to answer a question the name should have answered.

- Classes — `repositories/` only: `OracleRepository`, `CrmRepository`, `Gpt<FeatureName>Repository`. A service has no class.
- In a repository the class names the moving part and the method names the action; in a service the function name carries both. A bare verb is not enough — `extract` says nothing, `extract_identity_from_statement_line` says what and from where. Repeating a word from the class name is fine when it makes the action readable.
- Features named by purpose only — never by number (`feature_10` → `<meaningful_name>`).
- Functions MUST NOT start with `_` and MUST have descriptive, meaningful names that convey their purpose.
- Constants use `UPPER_SNAKE_CASE`, descriptive names.

## SECTION 3: LAYER PLACEMENT — WHERE DOES X LIVE

> Why one home per concern: every external dependency stays swappable and auditable from a single file. Searching one file answers "what SQL do we run", "what do we send to CRM", "what do we prompt the model" — a guarantee that leaked SQL or a stray CRM call destroys.

- **SQL** → `oracle_repository.py` and nowhere else — not in a service, a route, or another repository. `text(...)` defined inside the method body, never at class or module level.
- **CRM API** → `crm_repository.py` and nowhere else. Whether a feature gets a dedicated method there or the service calls `CrmRepository.send_to_crm()` with the payload inline is the trivial-wrapper threshold in [`03-code-quality.md`](03-code-quality.md) Section 5.
- **Prompts** → inline inside the GPT repository method only, never a file or a directory of their own. What the prompt must contain and how the response is read are [`12-repositories.md`](12-repositories.md) Section E; the full shape is [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py).
- **`<ResponseModel>`** → a class in the shared `schemas/gpt_responses.py` only.
- **Constants** → `conts.py` per microservice. Never inline in functions/classes.

## SECTION 4: ORCHESTRATOR CONTRACT

> Why `task_data` + `flow_id` travel whole: every layer logs the same full context to Splunk, so one `flow_id` reconstructs an entire run. Unpacking into positional fields — or rebuilding a smaller dict at the call site — breaks that trace and forces a signature change on every layer whenever a field is added.

- Calls only services/repositories. No inline helpers, business logic, or prompts.
- New feature = exactly one new call to `run_<feature_name>(task_data, flow_id)`.
- `task_data` and `flow_id` MUST flow through ALL layers: orchestrator → service → repository. Each layer extracts only what it needs from `task_data`.
- Every service/repository call receives the caller's FULL `task_data`. Never build a reduced dict at the call site and pass it as `task_data`.
- **Exception:** write payloads (SQL bind params, CRM body) are purpose-built dicts, not `task_data`.

**BAD:** `run_<feature_name>(field_a, field_b, flow_id)`
**GOOD:** `run_<feature_name>(task_data, flow_id)`

**BAD:** `<repository_method>({"field_a": task_data["field_a"], "field_b": task_data["field_b"]}, flow_id)`
**GOOD:** `<repository_method>(task_data, flow_id)`

## SECTION 5: SERVICE ENTRY-POINT CONTRACT

> Why the entry-point stays logic-free and last: reading the bottom of the file gives the whole feature flow in one screen, and every step above it can be read or changed in isolation.

- Entry-point: `run_<feature_name>(task_data, flow_id)` — MUST be the LAST function in the file.
- The `run_` prefix marks the entry point and nothing else. Every helper above it is named by a **verb phrase that describes the action**, not a bare verb — `load_statement_batch`, `select_self_employed_lines`, `extract_identity_from_statement_line`, `match_identity_to_fund_account`, `enrich_statement_line_from_emails`, `write_wide_interface_row`, `archive_processed_statement_files`.
- Read the call site out loud. `extract(...)` — extract *what*, from *where*? If the call site does not answer that, the name is wrong.
- Contains zero inline logic — only calls sub-functions sequentially (readable "table of contents"), and no conditionals beyond simple gating.
- All helpers defined above it. Max 2 levels deep. No deep chains `A→B→C→D` — flatten. Each sub-function does one complete, self-contained piece of work.
- Callers import the entry point by name: `from ..services.<feature_name>_service import run_<feature_name>`. Only the entry point is ever imported — the helpers above it stay private to the file.
