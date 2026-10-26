---
paths:
  - "*/scripts/**/*"
---

# scripts/ — Shared-Root Standards

> Operational helper scripts for running the workspace — starting servers, resetting a database, and
> similar chores. Shared root only; a service root never grows one
> ([`05-service-shape.md`](05-service-shape.md)).
> **Scope:** what a script here may do and touch. How the unit a script drives is built is decided by
> the phase rules, which do not govern this directory.

## SECTION 1: ONE SCRIPT, ONE CHORE

> Why: these scripts are run by hand under time pressure, usually while something is already broken. A
> script that does two things has no safe half to run.

- One script per chore, named for the verb it performs (`run_<what>.sh`, `reset_<what>.py`).
- Pick the language per chore: `.sh` for shell work — launching a process, installing dependencies;
  `.py` when the chore needs real logic — a database connection, parsing, branching.
- Keep it to the simplest form that does the chore. Add a flag, a config file or a target list only
  when the chore actually needs one.
- Read every credential and connection string from the `.env` of the unit the script drives.
- Fail loudly: exit non-zero and say which step failed.

## SECTION 2: PRODUCTION CODE IS READ-ONLY

> Why: a helper script that edits a service is an untracked, unreviewed change to a deployable — it
> lands in no diff and no SDD.

- A script invokes, inspects and resets external state — processes, databases, caches, local output
  folders.
- Leave every file under a service root untouched. Reading one is fine; writing one is not.

## Forbidden in this directory

- No application or business logic — a chore a service needs at runtime belongs in that service's
  `src/`.
- No script imported by a service, and no service module imported here.
- No hard-coded credential, connection string, host or certificate path.
- No writing to any file under a service root.

## REVIEW CHECKLIST

- [ ] One chore per script, named for the verb it performs (Section 1)
- [ ] Language matches the chore — `.sh` for shell, `.py` for logic (Section 1)
- [ ] Config and credentials come from `.env`, never the script body (Section 1)
- [ ] Failure exits non-zero and names the step (Section 1)
- [ ] Nothing under a service root is written (Section 2)
