---
paths:
  - "*/src/services/**/*"
---

# services/ — Layer Standards

> The file name, the entry-point contract and the `task_data` / `flow_id` flow are
> [`02-code-layout.md`](02-code-layout.md) Sections 1, 4 and 5. Error handling and safe defaults are
> [`04-error-and-logging.md`](04-error-and-logging.md). This file carries only what is true of the
> service layer and of nowhere else.

## Purpose
Business-flow orchestration. Each file owns one feature end-to-end. A service coordinates repositories
and never reaches an external system itself.

## Coding Rules (specific to this directory)
- **Confidence-score filtering happens here.** The GPT repository returns every item with its score; this layer keeps `score >= MIN_CONFIDENCE_THRESHOLD` (`src/conts.py`, value `4`) and drops the rest. Items below the threshold are never persisted and never sent to CRM — what counts as good enough is a business decision, and it does not belong to a repository.

## Forbidden in this directory
- No client, engine or session construction of its own — no `AzureOpenAI`, no SQLAlchemy engine, no `requests` session. Every external system is reached through its repository.
