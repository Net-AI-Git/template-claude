---
paths:
  - "*/tests/**/*"
---

# tests/ — Directory Standards

> Applies to every `tests/` directory in the workspace — inside a service root and inside the shared root alike.

## Purpose
Workspace for **named test scenarios / experiments**. Every distinct task that has its own test fixtures, scripts, or analysis gets its **own subdirectory** under `tests/`. This is not a traditional `pytest` mirror tree — each subdirectory is a self-contained experiment package. The reserved `pytest_business_logic/` container below is the one exception.

## Layout — One Subdirectory per Test/Experiment

```
tests/
├── tmp/                          ← shared root only — scratch workspace for ad-hoc model experiments (throwaway)
├── pytest_business_logic/        ← reserved container for guard tests (see its own section)
├── <test_name>/                  ← one directory per scenario, snake_case
│   ├── README.md                 ← describes this specific test (REQUIRED)
│   ├── inputs/                   ← fixtures consumed by the test
│   ├── outputs/                  ← captured artifacts (logs, generated files) — gitignored if large
│   └── test_<name>.py            ← entry-point script or pytest module
└── another_test/
    └── ...
```

## Scratch Workspace — `tmp/`
- All ad-hoc files the model creates or runs during an experiment, for any service, MUST live flat (no sub-directories) in the shared root's `tests/tmp/`. A service root has no `tests/tmp/`.
- Run a scratch file against a service from that service root: `PYTHONPATH=. .venv/Scripts/python ../<shared root>/tests/tmp/<file>.py`.
- Contents of `tmp/` are throwaway — no `README.md`, no commitment to preserve.
- Do NOT write scratch files anywhere else in the repo. Do NOT promote a `tmp/` file to a real test — recreate it under a proper `<test_name>/` subdirectory instead.

## Reserved Container — `pytest_business_logic/`

> Why: a large refactor silently drops business logic nobody wrote down. These tests are the record
> that fails when it happens.

`tests/pytest_business_logic/` is a regression suite, not an experiment package. The one-subdirectory-per-test
model above does not apply to it.

```
tests/pytest_business_logic/
└── <feature_name>/               ← one directory per feature, snake_case
    ├── README.md                 ← REQUIRED
    └── test_<feature_name>_logic.py
```

- Written only by the `preserve-business-logic` skill, from behaviors the user named. Never invented.
- Framework is `pytest`.
- Each test locks **one** named behavior and asserts **both** the returned value **and** the calls made to the repositories (order and arguments). Asserting only one of the two is incomplete.
- Against a non-deterministic source, assert the invariant the behavior guarantees — a field's presence, a type, a bound, an ordering, a branch taken — never an exact response string. An exact-match assertion on model output fails on variance, not on drift.
- The whole suite runs as one command from the service root: `.venv/Scripts/python -m pytest tests/pytest_business_logic -q`.
- Every feature directory here has a matching preserved-logic record under the shared root's `docs/spec/`. A guard test with no record, or a record with no guard test, is a defect.

## Coding Rules (specific to this directory)
- **Starting a new test = creating a new subdirectory**. Do NOT append unrelated test scripts to an existing test directory.
- Subdirectory name is the test name in `snake_case` (e.g. `invoice_extraction_v2/`, `prompt_ablation_seed_151/`).
- **Each test subdirectory contains a `README.md`** — never a `CLAUDE.md`.
- A subdirectory contains everything the test needs: fixtures, scripts, expected outputs, notes. No shared "global" fixtures pool — duplicate small fixtures across tests rather than coupling them.
- If two tests genuinely share large fixtures, place those fixtures in the owning service's `src/data/` and import — do not invent a top-level `tests/fixtures/` directory.
- **Every external system is called for real** — Oracle, Azure OpenAI, CRM, Redis, Splunk, filesystem. A test exercises the live path or it does not run.
- A test that is no longer relevant is **archived** (move into `tests/_archive/<name>/`), not deleted — historical results matter. A guard test under `pytest_business_logic/` is exempt while its `docs/spec/` record is live.

## Required `README.md` inside each test subdirectory
Each `<test_name>/README.md` must include:
- **Goal** — one sentence: what hypothesis or behavior this test verifies.
- **Scope** — which files under the owning service's `src/` are exercised.
- **How to run** — every terminal command required to reproduce the experiment end-to-end (env setup, install, data prep, execution), each on its own line, copy-paste runnable by an LLM with zero inference.
- **Inputs** — what is in `inputs/` and where it came from.
- **Expected outcome** — what success looks like.
- **Status** — `Active` / `Passing` / `Failing` / `Archived` + date of last run.

## Forbidden in this directory

> Why: a mocked dependency asserts that the mock behaves as written, never that the system does. The
> failures worth catching — a changed API shape, an expired credential, a model that stopped returning
> a field — are exactly the ones a mock hides.

- **No mocks, stubs, fakes, monkeypatching of a client, or recorded/replayed responses — anywhere under `tests/`.** This includes `unittest.mock`, `pytest-mock`, `responses`, `vcrpy` and hand-rolled doubles.
- No `test_<feature>.py` files at the **top level** of `tests/` — every test belongs inside its own subdirectory.
- No imports of test code from production modules under a service's `src/`.
- No tests that depend on execution order across subdirectories.
- No `print(...)` left in committed test code — use the framework's reporting.

## REVIEW CHECKLIST

- [ ] Every test lives in its own subdirectory — nothing at the top level of `tests/` (§Layout, §Forbidden)
- [ ] Each subdirectory carries a `README.md`, never a `CLAUDE.md` (§Coding Rules)
- [ ] That `README.md` has all six sections (§Required `README.md`)
- [ ] Scratch files are flat in the shared root's `tests/tmp/` and nowhere else; no service root has `tests/tmp/` (§Scratch Workspace)
- [ ] Every external system is called for real — no mock, stub, fake or recorded response anywhere (§Coding Rules, §Forbidden)
- [ ] Assertions against a non-deterministic source check an invariant, not an exact string (§Reserved Container)
- [ ] A guard test sits at `pytest_business_logic/<feature_name>/`, asserts both the returned value and the repository calls, and has a live `docs/spec/` record (§Reserved Container)
- [ ] No `print(...)` and no order dependency across subdirectories (§Forbidden)
