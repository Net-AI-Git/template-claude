# Phase 0b — Service Shape (applies to every service root)

> A **service root** is any directory containing `src/`. This file states what is true of every one of
> them. What is true of *one* service — its name, what it does, which layers it actually uses — lives in
> that service's own `CLAUDE.md`, which the team owns and edits.

## What a service root is

One deployable microservice, cloned from the shared template. Self-contained: nothing in it imports from
a sibling service, and nothing in it is imported by one. Each service owns its own copy of every file
under it — never edit one service expecting the change to reach another, and never assume two services
still match.

## Shape — the template ships both, each service keeps one

- **FastAPI** — `main.py` builds the app and includes the routers from `src/routes/`. Served with
  `uvicorn main:app`. Keeps `static/`.
- **Cron** — the entry point runs once and exits. No server, no `src/routes/`, no `static/`. The
  entry-point filename names the service (`run_<service_name>_cron.py`).

Same for layers: a service that never calls CRM or Redis deletes those repositories. A deleted layer's
rules apply again the moment it is added back.

## Forbidden in a service root

- No `docs/`, `plans/`, `splunk_dashboard/`, `postman/`, `evaluations/`, `notebooks/`, `scripts/`,
  `tests/tmp/` — those are shared and live under the shared root.
- No imports from a sibling service. Duplication across services is correct; a shared package is not.
- No new top-level directories without asking — the template layout is the contract.
- `.env` is copied from `.env.example` and filled locally. Never committed.
- No `certificates/`. A client certificate is located through `SOA_CERT_PATH`, never through a path
  built relative to the service root, so the service stays self-contained wherever the file is mounted.
  The file itself is never committed, in any root.
- `static/` holds third-party assets kept for offline / air-gapped environments. Replace the whole file
  when upgrading — never hand-edit minified vendor code.
