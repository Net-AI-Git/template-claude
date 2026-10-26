# Official Project Ruleset — Microservices

> These rules are MANDATORY. `00`, `01` and `05` load at every session start and stay resident. Every other rule carries `paths:` frontmatter and loads when a file it governs is read — a task that starts by **writing** a new file loads nothing, so read the matching rule file first (`01-teach-lesson.md` Section 2 maps task type to file). **After `/compact` they are gone until a file they govern is read again — re-read the file, or the rule, before continuing.** They are not reference documents — they are binding standards. All generated and reviewed code MUST comply.

## Phase Rules (apply in order)

1. [`01-teach-lesson.md`](01-teach-lesson.md) — Phase 0: pointer index — what to read before building a feature/repository/service/DB/Splunk/monitor/Redis. Consult its Section 2 map to find the files that govern the task type at hand.
2. [`05-service-shape.md`](05-service-shape.md) — Phase 0b: what is true of every service root — FastAPI vs Cron shape, self-containment, what a service root may never grow.
3. [`02-code-layout.md`](02-code-layout.md) — Phase 1: file structure, naming conventions, layer placement, orchestrator + service entry-point contracts. Apply when **writing new code, creating files, or implementing a feature**.
4. [`03-code-quality.md`](03-code-quality.md) — Phase 2: function size, formatting, variable hygiene, control flow, minimal code, data safety. Apply **after code is written**.
5. [`04-error-and-logging.md`](04-error-and-logging.md) — Phase 3: single try/except pattern, Splunk logging, no silent failures. Apply **after code works (hardening)**.
6. [`06-container-build.md`](06-container-build.md) — Phase 5: what a Dockerfile must look like once the change is approved. Apply when **touching any Docker file**.

Actions requiring explicit approval — SDD and waiver edits, `splunk_repository.py`, Docker files,
dependency manifests, shell commands — are enforced by `permissions.ask` in `.claude/settings.json`,
not by a rule file.

## Vocabulary — resolved by structure, never by name

This ruleset is self-contained: it resolves its own terms and depends on no file outside `.claude/`.

- **service root** — any directory containing `src/`. Every path in this ruleset written without a
  leading `*/` is relative to a service root. A service root never contains `docs/` or `plans/`.
- **shared root** — the directory matching `*/plans/`; the same directory holds `docs/SDD/` and
  `docs/spec/`. There is exactly one. If the glob matches zero or more than one, stop and ask.
- No rule file writes a directory name. Locate a root by its marker, not by memory.

## Directory Rules (`paths:`-scoped, one per directory)

Each directory's standards live in this folder and load when a file matching its `paths:` glob is read —
not when one is written or created there. There are no `CLAUDE.md` files next to the code.

| Rule | Loads on |
|---|---|
| [`10-src-package.md`](10-src-package.md) | `*/src/*.py` |
| [`11-services.md`](11-services.md) | `*/src/services/*.py` |
| [`12-repositories.md`](12-repositories.md) | `*/src/repositories/*.py` |
| [`13-routes.md`](13-routes.md) | `*/src/routes/*.py` |
| [`14-schemas.md`](14-schemas.md) | `*/src/schemas/*.py` |
| [`15-data.md`](15-data.md) | `*/src/data/**`, `*/evaluations/**` |
| [`16-notebooks.md`](16-notebooks.md) | `*/notebooks/**` |
| [`17-tests.md`](17-tests.md) | `*/tests/**` |
| [`20-docs-sdd.md`](20-docs-sdd.md) | `*/docs/**` |
| [`21-plans.md`](21-plans.md) | `*/plans/**` |
| [`22-postman.md`](22-postman.md) | `*/postman/**` |
| [`23-splunk-dashboard.md`](23-splunk-dashboard.md) | `*/splunk_dashboard/**` |
| [`24-splunk-audit.md`](24-splunk-audit.md) | `*/splunk_audit/**` |
| [`25-scripts.md`](25-scripts.md) | `*/scripts/**` |

Every glob is anchored one level below the workspace root, so **Claude must be started from the
workspace root** for these to load.

A service root also carries its own `CLAUDE.md` — a short identity card the team owns, stating what
*that* service is and which layers it uses. It carries no rules and never overrides this folder.

## Reference Implementation

- [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py) — the canonical GPT repository implementation that all `gpt_<feature_name>_repository.py` files MUST mirror.
- [`reference/Dockerfile.cron`](reference/Dockerfile.cron) · [`reference/Dockerfile.fastapi`](reference/Dockerfile.fastapi) — the two container templates. Every Dockerfile starts from one of them.

## Universal constraints

- **Nothing secret is ever committed** — no credential, token, certificate, connection string, real customer datum or PII, in any file of any root. The directory rules below do not restate this.
- **Each standard is stated once, in the file that owns its concern.** A directory rule (`10`–`24`) carries only what is true of that directory alone; everything else lives in the phase rules above. A standard you expect in a directory file and cannot find is in the phase rule that owns it — it still applies.

## Enforcement

- When generating code: read Phase 0 → follow Phase 1 → review against Phase 2 → harden with Phase 3.
- When any conflict arises, the stricter, more specific rule wins.
- An approved waiver document under the shared root's `docs/spec/` (`**/docs/spec/`) may explicitly waive a named standard for the file(s) it scopes; that waiver overrides the standard only where stated. A waiver whose scoped files no longer exist is void — check before relying on one.
