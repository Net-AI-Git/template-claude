---
name: preserve-business-logic
description: Captures the business logic a user wants locked against future refactors after production code is written in a service root, and enforces it in three places — a guard test under that service root's `tests/pytest_business_logic/`, a preserved-logic record under the shared root's `docs/spec/`, and a pointer line in auto-memory. Use when production code under a service root's `src/` has just been written or changed and the user should be asked what must not drift, when the user asks to lock, protect, freeze, or guard business logic, or when the business-logic guard hook asks for it.
---

# preserve-business-logic

## Purpose
Turn business logic that exists only in the user's head into something a later refactor cannot silently drop. The user names the behaviors; this skill writes a guard test that fails when one breaks, records the behavior under the shared root's `docs/spec/` so code review honors it, and leaves a pointer in auto-memory so the next session knows the guard exists.

## Required Input
- The service root whose `src/` changed. Derive it from the changed files; if two service roots changed → ask which one, then stop.
- The feature name, in `snake_case`. Derive it from the changed service or orchestrator file name; if it cannot be derived → ask.
- Which behaviors must be preserved. Never assume — always ask, per the Procedure.

## Procedure

### Step 1 — Establish the change set
Run `git status --porcelain` and `git diff HEAD`. Keep only paths matching `*/src/**/*.py`, `*/main.py`, `*/run_*.py`. Nothing matches → say so and stop; most invocations end here.

### Step 2 — Resolve the service root and the feature
The service root is the directory containing `src/`. The feature name is `snake_case`, taken from the changed service or orchestrator file. One service root only.

### Step 3 — Extract candidate behaviors
Read the changed lines and name each concrete behavior — a rule, a threshold, an ordering, a fallback, a guard clause — in one sentence saying what it does.

### Step 4 — Ask which behaviors to lock
Ask through `AskUserQuestion`, one atomic question per candidate, each with a "not this one" option. Never bundle two candidates into one question. The user may name a behavior not in the list. Nothing confirmed → skip to Step 8.

### Step 5 — Write the guard test
For each confirmed behavior, write or extend `tests/pytest_business_logic/<feature_name>/test_<feature_name>_logic.py` under that service root, following `${CLAUDE_PROJECT_DIR}/.claude/rules/17-tests.md` section "Reserved Container — `pytest_business_logic/`". One test per behavior, named after it. Then write or update `tests/pytest_business_logic/<feature_name>/README.md` with the sections that rule requires.

### Step 6 — Run the suite
Run `.venv/Scripts/python -m pytest tests/pytest_business_logic -q` from the service root and report the output verbatim. Failing → fix the test, not the production code, and run again. `pytest` missing → tell the user to run `poetry install` and stop before Steps 7 and 8.

### Step 7 — Record the spec
Invoke the `document-spec` skill with each confirmed behavior as a **preserved logic** record, scoped to the exact changed `src/` file path(s), the approver being the user who answered Step 4, and the approval date being today. Include the guard test path in each record's reason.

### Step 8 — Leave the pointers
Append one pointer line per feature to `preserved-business-logic.md` in the project's auto-memory directory, and index that file once in `MEMORY.md` — feature name, spec document path, guard test path, nothing else. Then append one line per handled `src/` file to `${CLAUDE_PROJECT_DIR}/.claude/.business-logic-asked`, formatted `<path-relative-to-workspace-root><TAB><sha1 of that file's current bytes>`. Both happen whether or not any behavior was confirmed.

### Step 9 — Report
The guard test path, the spec document path, and the test run result. Nothing else.

## Gotchas
- The hook that invokes this skill fires on any `src/` edit, including ones that carry no business logic at all — a constant, a rename, a log line. Step 4 offering only "not this one" is the expected outcome, not a failed run.
- `document-spec` stops when the approver or the approval date is implicit. Pass both explicitly in Step 7 or the spec is never written and the guard test is left without its record.
- Asserting only the return value passes for the wrong reason: a refactor that reorders the repository calls still returns the same value. Assert the calls too, per the rule.
- Calls are live, so the suite needs a filled `.env` and reachable systems, and a run costs real time and real tokens. A guard test that asserts an exact LLM response string will go red on model variance and block the turn for a reason that is not drift — assert the invariant instead.
- The state file is keyed by content hash, not path. Editing a locked file again re-triggers the ask — that is intended, and answering "not this one" costs one keystroke.

## Hard Prohibitions
- NEVER write a guard test for a behavior the user did not confirm in Step 4.
- NEVER write outside the one service root resolved in Step 2, plus the shared root's `docs/spec/`, auto-memory, and the state file.
- NEVER copy the behavior's text into auto-memory — the memory line is pointers only.
- NEVER report a test as passing without having run it in Step 6.
- NEVER change production code to make a guard test pass.
- NEVER mock, stub, fake or replay an external system in a guard test — every call is live, per `17-tests.md` §Forbidden.
- NEVER skip Step 8, including when the user confirms nothing.
- NEVER write the `docs/spec/` document directly — it is authored by `document-spec`.

## When to Ask Instead of Acting
- More than one service root changed → ask which one, then stop.
- The feature name cannot be derived from the changed files → ask, then stop.
- A behavior the user named is too vague to assert on → ask for the concrete input and expected outcome, then stop.
- The behavior spans two service roots → ask which one owns it, then stop.
- A guard test already exists for the feature and the new behavior contradicts one already locked → surface both, ask which wins, then stop.
