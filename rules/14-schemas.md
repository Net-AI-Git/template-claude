---
paths:
  - "*/src/schemas/**/*"
---

# schemas/ — Layer Standards

## Purpose
All Pydantic `BaseModel` declarations. Schemas describe data shapes flowing between layers and across the API boundary — they have no behavior.

## Coding Rules (specific to this directory)
- **One file per kind, several classes per file** — never a file per model or per feature: `api.py` (the shared `Request` / `Response`, reused across every feature), `gpt_responses.py` (LLM `response_format` models), `db_rows.py` (persisted table-row models). A new file is justified only by a new kind.
- A `response_format` model whose top level is a list needs a wrapper model holding that list as one field.
- `BaseModel` subclasses only. **Type annotations are mandatory here** — Pydantic requires them.
- Field defaults expressed via `Optional[...] = None` or `Field(...)` — keep it minimal.

## Forbidden in this directory
- No business logic — no methods beyond Pydantic validators when strictly necessary.
- No DB session imports, no HTTP clients, no OpenAI imports.
- No inheritance chains deeper than one level beyond `BaseModel`.