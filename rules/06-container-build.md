---
paths:
  - "*/Dockerfile*"
  - "*/docker-compose.{yaml,yml}"
  - "*/.dockerignore"
  - "**/reference/Dockerfile*"
---

# Phase 5 — Container Build

> Changing any Docker file still requires explicit approval — `permissions.ask` in `.claude/settings.json` gates the change, this file says what the change must look like.
> Templates: [`reference/Dockerfile.cron`](reference/Dockerfile.cron) · [`reference/Dockerfile.fastapi`](reference/Dockerfile.fastapi)

## SECTION 1: START FROM THE TEMPLATE

Two service shapes exist. Pick the matching template and fill in the placeholders — do not write a Dockerfile from memory.

| Shape | Template | Behaviour |
|---|---|---|
| Cron | [`reference/Dockerfile.cron`](reference/Dockerfile.cron) | Runs, exits. No server, no port |
| FastAPI | [`reference/Dockerfile.fastapi`](reference/Dockerfile.fastapi) | Stays up, serves HTTP |

A third shape is not invented without asking.

## SECTION 2: WHAT GOES IN THE IMAGE

> Why explicit: `COPY . .` copies whatever is in the working directory on the day it is built. That set grows — IDE folders, run artefacts, crash dumps, test data, `.git`. The image is then a moving target that nobody reviews, and the only thing standing between it and a leaked credential is a `.dockerignore` nobody re-reads.

- **Never `COPY . .`.** Copy the named paths the service needs: dependency manifests, the package directory, the entry point.
- **The runtime stage copies from the builder**, by path, never from the build context again.
- **`.dockerignore` is a second line of defence, not the first.** It is checked against what it actually matches — a pattern that looks right and matches nothing is worse than no pattern, because it is believed. `git*` does not match `.git`.
- **Never in the image:** `.env` or any credential file, real data, test fixtures, `.git`, IDE directories, dashboards, docs, crash dumps.
- **Configuration is injected at runtime.** A baked `.env` silently overrides the platform's values through `load_dotenv()`, and the failure looks like a config bug in production.

## SECTION 3: THE ENV BLOCK

- `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1` in **both** stages.
- A runtime stage missing `PYTHONUNBUFFERED` buffers stdout. When the process dies the buffer goes with it — the last output before a failure is exactly what is lost, and the run looks like it stopped for no reason.

## SECTION 4: THE ENTRY POINT

- **Cron shape:** the entry-point filename names the service — `run_<service_name>_cron.py`. Not `run_cron.py`.
- **FastAPI shape:** the entry point is `main.py`, the uvicorn convention the template is built on. The service is named by the image and the `CMD`, not the filename.
- With two repos open, a generic name says nothing in a process list, a log line, or a `CMD`.
- The name appears in the Dockerfile. Renaming the file is a Docker change and takes approval with it.

## SECTION 5: DEPENDENCY LAYERS

- Manifests are copied and installed **before** application code, so a code change does not reinstall dependencies.
- `poetry.lock` is copied with `pyproject.toml`. Installing without the lock resolves fresh versions at build time and the image stops being reproducible.
- `--only main` — dev dependencies do not ship.

## REVIEW CHECKLIST
- [ ] Built from the matching template (Section 1)
- [ ] No `COPY . .` in either stage (Section 2)
- [ ] `.dockerignore` patterns verified against what they match (Section 2)
- [ ] No `.env`, credentials, data, `.git` or IDE directories in the image (Section 2)
- [ ] ENV block present in both stages (Section 3)
- [ ] Entry-point filename names the service (Section 4)
- [ ] Manifests copied and installed before application code; `poetry.lock` present (Section 5)
- [ ] Change approved before it was made (`permissions.ask`)
