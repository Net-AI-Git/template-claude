---
paths:
  - "*/plans/**/*"
---

# plans/ — Shared-Root Standards

## Purpose
Planning documents for upcoming work — feature designs, refactor proposals, migration plans. **Pre-implementation** artifacts. Once a plan is executed, the resulting truth lives in code + the relevant per-feature SDD under the shared root's `docs/`, not here.

## Coding Rules (specific to this directory)
- One `.md` file per plan, named `<topic>.md` (e.g. `monitoring-rollout.md`, `gpt-prompt-migration.md`).
- Status indicator at the top of each plan: `Draft` / `Approved` / `In Progress` / `Done` / `Archived`.
- Plans are scoped, time-bound documents — not living rules.
- A plan must specify: goal, scope (files touched), out-of-scope, success criteria, rollback strategy, **and which feature SDD(s) it will update**.
- When a plan ships, change its status to `Done` and add a one-line link to the resulting code + the updated `<feature>/SDD.<ext>`. Keep the file for history.
- Stale plans (`Draft` > 30 days untouched) get marked `Archived` and moved to `plans/archive/` if that subdirectory exists, otherwise stay in place with the `Archived` tag.
- Plans never override this ruleset. If a plan needs to violate a rule, surface the conflict explicitly — do not bake the violation into the plan.

## Forbidden in this directory
- No executable code, no scripts.
- No duplication of per-feature SDD content — plans propose changes; the SDDs record what exists.
- No undated plans without an author and a target completion date.
