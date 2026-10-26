---
paths:
  - "*/docs/SDD/**/*"
  - "*/docs/spec/**/*"
  - "*/docs/testing-process/**/*"
  - "*/docs/splunk.md"
---

# docs/ — Shared-Root Standards

> The shared root is the directory matching `*/plans/`; the same directory holds `docs/SDD/` and
> `docs/spec/`. There is exactly one. If the glob matches zero or more than one, stop and ask.

## Purpose
Architectural and operational documentation. The authoritative source for **what each feature is and why it is the way it is** — distinct from this ruleset, which governs **how to write code**.

## Layout — One SDD per Feature

```
docs/
├── splunk.md                         ← cross-cutting operational guides
├── spec/                             ← approved spec/waiver documents
├── testing-process/                  ← one test-process doc per feature (feature-test-doc skill)
│   └── <feature_name>.md
└── SDD/                              ← all SDDs live here
    ├── <feature_name>/               ← one directory per feature
    │   ├── SDD.<ext>                 ← the feature's Software Design Document
    │   ├── diagrams/                 ← optional Mermaid / images
    │   └── notes.md                  ← optional extra context
    └── another_feature/
        └── SDD.<ext>
```

- **All SDDs live under `SDD/`** — never at the top of `docs/`.
- **Each feature owns its own SDD**, not the project as a whole. A "feature" here means a coherent business capability.
- The SDD file format is **not constrained by this directory** — `.md`, `.docx`, or any other format produced by the team's tooling is acceptable. The internal structure of the SDD is decided by its authors, not enforced here.
- Cross-feature concerns (Splunk conventions, deployment runbooks) live as top-level `*.md` files in `docs/`.
- When the `sync-sdd` skill runs, it asks **which** SDD to reconcile against — there is no single global SDD.
- **Approved spec/waiver documents live under `spec/`** — authored by the `document-spec` skill. Each records intentional, approved decisions (approved deviations from a named standard, or business logic to preserve) scoped to specific files, and directs code review to honor them.
- **Test-process docs live under `testing-process/`** — authored by the `feature-test-doc` skill. One `<feature_name>.md` per feature, plain-English (no code), explaining end-to-end how that feature is tested; updated in place when the feature's code changes.

## Coding Rules (specific to this directory)
- One SDD per feature, all under `SDD/`. Do NOT create a single project-wide `SDD.*`. Cross-feature material goes into a topic-specific `.md` at the top of `docs/` (like `splunk.md`).
- Feature directory name = feature name in `snake_case`, matches the service file name where reasonable (e.g. `SDD/<feature_name>/` ↔ the owning service's `src/services/<feature_name>_service.py` if that is the entry-point).
- The SDD's **internal structure is the author's choice** — markdown, Word, hand-drawn diagrams, whatever the team uses. This file does NOT prescribe sections.
- Every architectural change in code requires a paired update to the **relevant** SDD — or, if the change spans features, to every SDD it touches.
- Diagrams: prefer Mermaid inline when authoring in `.md`; place binary assets in `SDD/<feature>/diagrams/`.
- Markdown links use paths relative to the linking file.

## Forbidden in this directory
- No code, no executable scripts, no test data.
- No duplication of this ruleset's content — those rules are operational law and live elsewhere. A `spec/` document may **cite** a named rule it waives, but never restates the ruleset.
- No SDD files outside `SDD/`, and no "global" SDD inside it — SDDs are per-feature.
- No silent rewrites of any SDD — every change must come from an explicit user decision (per the `sync-sdd` conflict-resolution flow).
- No two SDDs claiming ownership of the same code path — if a file is shared, one feature owns it and the others cross-reference.
