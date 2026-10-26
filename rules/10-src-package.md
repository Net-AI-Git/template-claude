---
paths:
  - "*/src/*.py"
---

# src/ — Package Root Standards

## Purpose
Root of the application package. Holds cross-cutting modules (config, constants, shared utils, FastAPI dependencies) and the layer directories.

## Coding Rules (specific to this directory)
- `config.py` holds runtime configuration only — env loading and settings objects.
- `conts.py` is where the constants placed by [`02-code-layout.md`](02-code-layout.md) Section 3 land. Anything used in ≥2 files moves here; inline duplication is a smell.
- `dependencies.py` is the **only** place FastAPI `Depends` factories live.
- Flat layout — do not create new feature-named subdirectories at this level.

## Forbidden in this directory
- No domain logic in `config.py` — that is infrastructure.
- No new top-level files that duplicate an existing concern.