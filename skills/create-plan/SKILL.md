---
name: create-plan
description: Draft an Implementation Plan markdown file under the workspace's shared `plans/` directory, named `<branch-name>.md`, via focused Q&A. Captures goal, success criteria, architectural decisions, and final deliverable before any code is written. Use when the user asks for a "plan", "implementation plan", "תוכנית", "תוכנית פעולה", or otherwise requests structured pre-implementation planning for an upcoming feature or change.
---

# create-plan

## Purpose

Produce a single, per-branch Implementation Plan under the shared root's `plans/` that records what the user wants to achieve, the constraints, the architectural decisions, and the final deliverable — **before** any code is written. One plan file per Git branch, shared across every service.

The **shared root** is the single top-level directory matching `*/plans/`; the same directory holds `docs/SDD/` and `docs/spec/`. Locate it by that marker, never by name. If the glob matches zero or more than one, stop and ask.

## Required Input

Ask for these in order. Ask **one focused question per turn**. Never guess, never run commands to derive an answer.

1. **Branch name** — the exact name of the Git branch the plan belongs to. Ask the user; do NOT run `git`, `git branch`, or any shell command to detect it.
2. **Goal** — one paragraph: what the user wants to achieve.
3. **Success Criteria** — bullet list: measurable conditions that mean the work is done.
4. **Architectural Decisions** — bullet list: layer placement, chosen patterns, libraries, integration points, trade-offs already decided.
5. **Scope** — in-scope files/areas + explicit out-of-scope items.
6. **Final Deliverable** — one paragraph: exactly what the finished artifact looks like (endpoints, files, behavior, output shape).
7. **SDD(s) impacted** — which per-feature SDD under the shared root's `docs/SDD/` this plan will update when shipped (per `${CLAUDE_PROJECT_DIR}/.claude/rules/21-plans.md`). If none → the user must say "none" explicitly.
8. **Rollback Strategy** — one line: how to revert if the change ships badly.

If the user provides multiple answers at once, use them and skip only the ones already answered.

## Procedure

### Step 1 — Get the branch name
- Ask the user for the branch name verbatim.
- Do NOT invoke the `Bash` tool for any reason during this step — `permissions.ask` in `${CLAUDE_PROJECT_DIR}/.claude/settings.json` prompts on every shell command.
- Sanitize the name for a filename: keep it as the user typed it, replacing `/` with `-` only if the branch contains slashes (e.g. `feature/foo` → `feature-foo.md`). Confirm the resulting filename back to the user in one line.

### Step 2 — Check if the plan file already exists
- Target path: the shared root's `plans/<branch-name>.md`.
- If the file exists → ask the user exactly: **append / overwrite / abort**, using the `AskUserQuestion` tool (one question, the three options as choices). Do NOT default. Wait for the choice.
  - `append` → new content is appended under a dated `## Revision — YYYY-MM-DD` section at the bottom; existing content is untouched.
  - `overwrite` → replace the file entirely with the new plan.
  - `abort` → stop the skill cleanly, write nothing.
- If the file does not exist → proceed.

### Step 3 — Gather plan content
- Walk through items 2–8 in **Required Input** with focused questions.
- Do not proceed to writing until every item has an answer (an explicit "none" counts as an answer).

### Step 4 — Write the plan
Use this exact template. Match the tone of `${CLAUDE_PROJECT_DIR}/.claude/rules/21-plans.md` — scoped, time-bound, no fluff.

```
# <Branch Name> — Implementation Plan

**Status:** Draft
**Author:** <ask the user; do not infer>
**Created:** <YYYY-MM-DD — ask the user; do not read the clock>
**Target Completion:** <ask the user; "TBD" is acceptable only if the user says so>

## Goal
<paragraph>

## Success Criteria
- <bullet>
- <bullet>

## Architectural Decisions
- <bullet>
- <bullet>

## Scope
**In:**
- <bullet>

**Out:**
- <bullet>

## Final Deliverable
<paragraph>

## SDD(s) Impacted
- <path under the shared root's docs/SDD/ or "none">

## Rollback Strategy
<one line>

## Open Questions
- <bullet or "none">
```

### Step 5 — Report
Reply with: the file path written, the branch name, and the plan `Status` line verbatim. Nothing else.

## Hard Prohibitions

- Do NOT run any shell command (`git`, `ls`, `dir`, `cat`, `type`, etc.) to detect the branch name or verify file existence — use the `Read` / `Glob` tools for existence, and ask the user for the branch. `permissions.ask` in `${CLAUDE_PROJECT_DIR}/.claude/settings.json` prompts on every shell command.
- Do NOT create the file without an explicit branch name from the user.
- Do NOT overwrite an existing plan without explicit `overwrite` confirmation.
- Do NOT invent goal/criteria/decisions the user did not state.
- Do NOT add sections beyond the template in Step 4.
- Do NOT touch any file other than the shared root's `plans/<branch-name>.md`.
- Do NOT bake rule violations into the plan — if the user's plan requires violating a rule under `${CLAUDE_PROJECT_DIR}/.claude/rules/`, surface the conflict in one sentence and stop.
- Do NOT begin implementation of the plan — this skill only writes the plan document.

## When to Ask Instead of Acting

- The branch name is missing or ambiguous.
- A file with the same branch name already exists (append / overwrite / abort).
- The user gives a goal or deliverable too vague to write down as one paragraph.
- The plan conflicts with `${CLAUDE_PROJECT_DIR}/.claude/rules/` or an existing SDD under the shared root's `docs/SDD/`.
- The user asks the skill to also implement the plan — clarify that this skill only drafts the plan.

Ask one focused question, then stop.
