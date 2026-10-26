---
paths:
  - "*/splunk_dashboard/**/*"
---

# splunk_dashboard/ — Shared-Root Standards

## Purpose
Version-controlled Splunk dashboard artifacts — exported dashboard definitions and the SPL queries that power them. Authored and consumed by humans (ops, dev, SRE). **Not loaded by the runtime** — no microservice ever reads from this directory.

## Coding Rules (specific to this directory)
- `*.xml` / `*.json` — dashboard definitions exported from Splunk (Simple XML or Dashboard Studio JSON), one file per dashboard.
- `*.spl` — standalone SPL queries that back panels in the exported dashboards (one query per file, or grouped by dashboard).
- Optional `README.md` per dashboard describing what it monitors, the source `index` / `sourcetype`, and the alerts wired to it.
- One dashboard per file. Filename = dashboard name in `snake_case` (e.g. `service_overview.xml`).
- Every dashboard file MUST have a matching `<name>.spl` (or a `queries/` subdir with the panel queries) so the SPL is reviewable without opening Splunk.
- SPL queries MUST consume logs produced by a service's `src/repositories/splunk_repository.py` — match the `status` / `flow_id` / `content` fields it emits, and respect the conventions in the shared root's `docs/splunk.md`. Each service has its own producer; a dashboard may span several.
- Re-export from Splunk after every meaningful change (new panel, query edit, layout change). Hand-editing exported XML/JSON is allowed only for trivial fixes (typos, tokens) — structural edits go through Splunk's UI then re-export.
- Dashboards reference indexes / sourcetypes via tokens (`$index$`, `$env$`) so the same file works across dev / staging / prod.
- When a code change alters log shape (new `status`, renamed field), the dashboards that read it MUST be updated in the same change set — never let dashboards silently break.

## Forbidden in this directory
- No executable code (`.py`, `.sh`).
- No runtime imports from here — no microservice may read these files at startup or request time.
- No hardcoded production hostnames — use Splunk tokens / environment variables.
- No dashboards built on `index=*` or `sourcetype=*` — every query MUST be scoped.
