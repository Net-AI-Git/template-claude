---
paths:
  - "*/src/data/**/*"
  - "*/evaluations/**/*"
---

# data/ — Directory Standards

## Purpose
Local fixtures, sample documents, and static datasets used for **manual testing and development only**. Not consumed by production code paths.

## Coding Rules (specific to this directory)
- Treat as **read-only at runtime** — production code MUST NOT import from this directory.
- Fixtures used by automated tests live under the service's `tests/`, not here.
- Sample documents are anonymized before they land here — real identifiers are replaced, not just hidden.
- New large binaries → check size before committing. Prefer `.gitignore` + a download script over committing > 1 MB blobs.

## Forbidden in this directory
- No imports **from** this directory into `services/`, `repositories/`, `routes/`, `schemas/`.
- No transient temp files (`~$*`, `*.tmp`) — those should be `.gitignore`d.
