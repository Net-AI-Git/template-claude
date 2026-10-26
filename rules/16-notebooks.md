---
paths:
  - "*/notebooks/**/*"
  - "*/src/**/*.ipynb"
---

# notebooks/ — Directory Standards

## Purpose
Jupyter notebooks for **experimentation only**: prompt tuning, evaluation, ad-hoc analysis. Not part of the runtime.

## Coding Rules (specific to this directory)
- One notebook per experiment, named by topic (e.g. `<experiment_name>_experimenting.ipynb`).
- Notebooks **must not** be imported by `services/`, `repositories/`, `routes/`, or `schemas/`.
- Notebooks **must not** be included in the Docker image — verify the service's `Dockerfile` and `.dockerignore` keep this directory out.
- Clear cell outputs before committing — an executed cell carries whatever it printed, including large binary blobs.
- Experimental code that proves valuable graduates to a proper module in `services/` or `repositories/` — the notebook stays as a historical record but is **not** the source of truth.

## Forbidden in this directory
- No reliance on outputs from this directory by any runtime module.
