# Phase 0 — Teach Lesson (Read Before Writing ANY Code)

> MANDATORY: This file governs every feature, repository, service, DB call, Splunk log, monitor query, and Redis call. It is a **pointer index** — it does not restate rules, only points to where each rule lives. It is unscoped because a task that starts by *writing* a new file loads no scoped rule at all ([`00-overview.md`](00-overview.md) explains the loading model). Use Section 2 to look up the files that govern the task type at hand, and read them when they are not already in context.
> Next phases: [`02-code-layout.md`](02-code-layout.md) → [`03-code-quality.md`](03-code-quality.md) → [`04-error-and-logging.md`](04-error-and-logging.md).

## SECTION 1: ARCHITECTURE (one-line map)

```
main.py → routes/ → services/ → repositories/ → external (Oracle / GPT / CRM / Redis / Splunk / filesystem)
                        ↑
                    schemas/ (Pydantic only)
```

`task_data` + `flow_id` flow through every layer. Constants live in `src/conts.py`.

Every row below applies to whichever layers the service actually has — which shape it takes and which
layers it keeps are decided in [`05-service-shape.md`](05-service-shape.md).

## SECTION 2: WHAT TO READ BEFORE EACH TASK
For every task type below, read the listed files **in order** before writing code.

- **New feature** → [`02-code-layout.md`](02-code-layout.md) Sections 1, 4, 5 → [`04-error-and-logging.md`](04-error-and-logging.md) → [`11-services.md`](11-services.md).
- **New service** → [`05-service-shape.md`](05-service-shape.md) → [`02-code-layout.md`](02-code-layout.md) Sections 2, 4, 5 → an existing `src/services/<feature_name>_service.py` as the shape reference → [`04-error-and-logging.md`](04-error-and-logging.md) → [`11-services.md`](11-services.md).
- **New repository (or new repo method)** → [`02-code-layout.md`](02-code-layout.md) Sections 1, 3 → [`04-error-and-logging.md`](04-error-and-logging.md) → [`12-repositories.md`](12-repositories.md).
- **DB connection / new Oracle method** → `src/repositories/oracle_repository.py` → [`02-code-layout.md`](02-code-layout.md) Section 3 (SQL placement) → [`12-repositories.md`](12-repositories.md) Section A. If the service deleted that layer from the template, ask before recreating it.
- **Splunk log** → [`04-error-and-logging.md`](04-error-and-logging.md) → `src/repositories/splunk_repository.py`.
- **Metrics / monitor query** → the shared root's `docs/splunk.md` (the metric convention) → `src/repositories/splunk_repository.py` (`publish_metrics`, `get_data_from_splunk`) → [`04-error-and-logging.md`](04-error-and-logging.md).
- **Dockerfile / container build** → [`06-container-build.md`](06-container-build.md) → the matching template in [`reference/`](reference/). Approval first (`permissions.ask`), then the template.
- **GPT / LLM repository** → [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py:1) → [`02-code-layout.md`](02-code-layout.md) Section 3 (prompts, response models) → [`12-repositories.md`](12-repositories.md) Sections B and E. If the service deleted that layer from the template, ask before recreating it.
- **Pydantic schema** → [`02-code-layout.md`](02-code-layout.md) Sections 1, 3 → [`14-schemas.md`](14-schemas.md).
- **Cross-cutting module (`config.py`, `conts.py`, `dependencies.py`)** → [`10-src-package.md`](10-src-package.md).
- **Docs / SDD / spec** → [`20-docs-sdd.md`](20-docs-sdd.md).
- **Plan** → [`21-plans.md`](21-plans.md).
- **Tests** → [`17-tests.md`](17-tests.md).
- **FastAPI route** → [`02-code-layout.md`](02-code-layout.md) Sections 1 and 3 (layer placement) → [`13-routes.md`](13-routes.md).
- **Static asset** → [`05-service-shape.md`](05-service-shape.md). Vendor files are replaced whole, never hand-edited.
- **CRM call / Redis usage** → [`02-code-layout.md`](02-code-layout.md) Sections 1 and 3 → [`12-repositories.md`](12-repositories.md) Section C. If the service deleted that layer from the template, ask before recreating it.
- **Fixture / sample data / notebook** → [`15-data.md`](15-data.md) · [`16-notebooks.md`](16-notebooks.md).
- **Splunk dashboard / audit pull** → [`23-splunk-dashboard.md`](23-splunk-dashboard.md) · [`24-splunk-audit.md`](24-splunk-audit.md).
- **Postman collection** → [`22-postman.md`](22-postman.md).

## SECTION 3: HARD RULE
- Never write code without completing the read list above for the matching task type.
- The read list is completed in this session. A summary returned by a subagent does not complete it — the built-in `Explore` and `Plan` agents do not load this ruleset, and no setting changes that.
- If a rule file and the existing code disagree → STOP, surface the conflict, do not pick a side.
- If the task does not match any row in Section 2 → ask, do not guess.
