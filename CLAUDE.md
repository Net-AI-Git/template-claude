# Workspace — Migdal AI Microservices

## What this workspace is

Every top-level directory is one independent unit, cloned from the same FastAPI template and
evolved separately. There is no shared package and no root build.

Two roles, told apart by structure — never by name:

| Role | What it is | How to recognise it |
|---|---|---|
| **service root** | A deployable service. Self-contained: its own `main.py`, `src/`, `tests/`, `Dockerfile`, `requirements.txt`, `pyproject.toml`, `.env`. | Any top-level directory that **contains `src/`**. There are several. |
| **shared root** | Shared, non-deployable infrastructure serving **all** services. | The single top-level directory matching `*/plans/`; the same directory holds `docs/SDD/` and `docs/spec/` and has **no `src/`**. If that glob matches zero or more than one, stop and ask. |

**Directory names are placeholders and change.** Locate a root by its marker, not by memory. Never write
a literal top-level directory name in `.claude/` — use name-free globs (`*/src/services/*.py`) and paths
relative to a unit root. Renaming a directory must never break anything.

Services start from the same template, then diverge. Each one owns its own copy of every file under
it — never edit one service expecting the change to reach another, and never assume two services
still match.

## Shared artifacts live in the shared root, never per service

| Artifact | Location under the shared root |
|---|---|
| SDD — one per feature | `docs/SDD/<feature_name>/` |
| Approved waivers / spec documents | `docs/spec/` |
| Test-process docs | `docs/testing-process/` |
| Implementation plans | `plans/` |
| Splunk dashboards | `splunk_dashboard/` |
| Splunk audit tooling | `splunk_audit/` |
| Operational helper scripts (run servers, reset a DB, …) | `scripts/` |
| Postman collections | `postman/` |
| Evaluation sets | `evaluations/` |
| Experimentation notebooks | `notebooks/` |
| Scratch files (throwaway, flat) | `tests/tmp/` |
| Client certificates (mount point; contents never committed) | `certificates/` |
| Cross-cutting operational guides | `docs/` |

A service root never grows its own `docs/`, `plans/`, `splunk_dashboard/`, `postman/`, `evaluations/`,
`notebooks/`, `scripts/`, or `tests/tmp/`.
When a skill or rule asks for "the SDD", "the plan", or "the spec", it means the one under the shared
root, named after the feature — not a per-service copy.

## The ruleset is law

[`.claude/rules/00-overview.md`](rules/00-overview.md) indexes the binding standards for writing code in
any service. They are not reference documents. Rules scoped with `paths:` frontmatter load when a
matching file is read; the rest load every session.

When a request conflicts with a rule: state the conflict in one sentence, stop, offer the
compliant path, wait. Never write rule-violating code silently.

## Change scope

- A change belongs to exactly **one** service root. Touching two service trees in a single change
  requires saying so first and waiting for approval.
- Duplication across services is expected and correct — they are separate deployables, not a
  shared library. Never extract common code into a root-level package.
- `dev-docs/` is a separate git repository checked out inside this workspace. Do not commit to it or
  edit it unless explicitly asked.
- `.claude/` is also its own git repository, pulled and pushed independently of the workspace. A change
  to rules, skills, settings or this file is committed there — never in the workspace repo.

## Record every cross-cutting decision

Auto memory is on by default and machine-local, at `~/.claude/projects/<project>/memory/`. The
`<project>` key is derived from the git repository, so every unit in this workspace shares one memory
directory. Nothing there is committed or distributed — only this instruction travels with the
template.

**Before continuing past a decision that applies beyond one file — layout, tooling, process, a rule
or a setting — append it to `decisions.md` in that directory.** Three lines, absolute date:

```
### YYYY-MM-DD — <what was decided>
**Why:** <the reason it was chosen>
**Rejected:** <the alternative> — <why it lost>
```

`MEMORY.md` beside it is the index — one line per topic file, and only the first 200 lines or 25KB
load each session. Detail goes in the topic file, never in the index.

Record the decision and its reason. Never record what a file already states: architecture, paths,
conventions, or anything already written under `.claude/`.

## Running a service

Every command runs from the service root, never from the workspace root:

```bash
cd <the service root you are working in>
pip install -r requirements.txt
poetry install
.venv/Scripts/python -m uvicorn main:app
```

Health check: `http://127.0.0.1:8000/api/ping`. Both commands fail without a filled `.env`.

## Where the standards live

All directory-scoped standards live in [`.claude/rules/`](rules/) and load automatically when Claude
reads a matching file — there are no `CLAUDE.md` files next to the code.

The one exception: each service root carries its own short `CLAUDE.md` — a service identity card
stating what *that* service is, which shape it takes, and which layers it uses. The team owns and edits
it. It carries no rules.

Writing or changing one of those files — a rule, a skill, this map, the output style — follows
[`prompt-authoring.md`](prompt-authoring.md): which mechanism holds which text, the rule and skill
templates, and what Claude Opus 5 needs said (and left unsaid). The four `create-`/`update-` skills
read it before they write.
