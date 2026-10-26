---
name: create-rule
description: Add a brand-new rule to `.claude/rules/` based on the user's exact request — minimal wording, no inference, no scope creep. If the subject already exists anywhere in `.claude/rules/`, stop and redirect to `update-rule`. Use when the user asks to add, introduce, or define a new rule under `.claude/rules/` (typical phrasing — "add a rule", "create a rule", "new rule for ...").
---

# create-rule

## Purpose

Insert a single new rule into `${CLAUDE_PROJECT_DIR}/.claude/rules/` that does not already exist anywhere in the ruleset. Refuse silently-overlapping additions — those belong to `update-rule`.

## Required Input

The exact rule the user wants, in their own words. Example: "every public service function must end with a single bare return".

If the wording is too vague to compress without losing meaning → ask one focused question, then stop.

## Procedure

### Step 1 — Confirm the rule is new
- Search **all files** in `${CLAUDE_PROJECT_DIR}/.claude/rules/` for every mention of the subject (rule text, examples, checklists, reference snippets).
- If even one hit exists → STOP. Tell the user to run `update-rule` instead. Do not proceed.

### Step 2 — Pick exactly one target location
- Choose the single most relevant rule file and the single most relevant section inside it.
- If two files or two sections seem equally relevant → ask, do not pick.
- Do NOT create a new rule file unilaterally — propose it and wait for approval.

### Step 3 — Write the rule
- Read `${CLAUDE_PROJECT_DIR}/.claude/prompt-authoring.md` first — it holds the writing standard every prompt under `.claude/` follows, including the rule-file template and the `paths:` targeting rules.
- Use the **fewest words** that convey the rule.
- State what to do, not only what not to do. The negative form belongs in the file's `Forbidden in this directory` section, where it is the point.
- Match the bullet style, indentation, and numbering of neighbouring rules in the chosen section.
- Write generically — never bind the rule to a specific feature name, service, or project. Use placeholders (e.g. `<feature_name>`, `<name>`) and general phrasing so it stays reusable when `.claude/` is copied to another project.
- No examples, no rationale, no preamble inside the rule bullet itself — unless the user explicitly asked for them. A rule bullet states the requirement, nothing more.
- **Exception — section-level motivation:** several sections in `${CLAUDE_PROJECT_DIR}/.claude/rules/` open with a `> Why ...` blockquote directly under the heading, explaining the constraint the section enforces. That block is part of the established format. When a *whole new section* is approved, one such blockquote is allowed; a rule added to an existing section never gets its own rationale.

### Step 3b — Only if a whole new rule file was approved in Step 2
Use this structure, matching the neighbouring rule files:

```
---
paths:
  - "<name-free glob, anchored one level below the project root>"
---

# <Directory or phase name> — <Layer / Phase> Standards

> One line placing this file in the chain: what came before, what comes next.
> **Scope:** what this file decides, and the one sentence naming what it leaves to another file.

## SECTION 1: <THE CONSTRAINT, NAMED>

> Why: the failure this section prevents — what breaks, for whom, and when.

- <one requirement per bullet, imperative, no rationale inside the bullet>

## Forbidden in this directory

- <the negative form of the same constraints>

## REVIEW CHECKLIST

- [ ] <one checkable line per requirement, each naming its section>
```

- `paths:` is the only frontmatter field Claude Code defines for a rule. Invent no others. A file with no `paths:` is resident in every session — choose that only for an index that must survive a task which starts by writing a new file.
- Register the new file in the table in `${CLAUDE_PROJECT_DIR}/.claude/rules/00-overview.md`. Then report — do not edit — that the scoping table in `${CLAUDE_PROJECT_DIR}/.claude/PORTABILITY.md` now needs the matching row.
- Never place a `.md` file under `${CLAUDE_PROJECT_DIR}/.claude/rules/reference/` — files there are discovered recursively and load as unscoped rules. That directory holds code templates only.

### Step 4 — Insert in one pass
- Touch ONLY the chosen section.
- Do not "harmonize", renumber, or rephrase unrelated rules.

### Step 5 — Report
Reply in chat with: the file changed, the section touched, and the new bullet verbatim. Nothing else.

## Hard Prohibitions

- Do NOT proceed if any existing hit was found in Step 1 — redirect to `update-rule`.
- Do NOT create a new rule file unilaterally — propose it and wait for approval.
- Do NOT extend the rule to cover cases the user didn't mention.
- Do NOT add corollaries, exceptions, or "while we're at it" edits.
- Do NOT rephrase neighbouring rules.
- Do NOT add explanations or rationale into the rule bullet itself — the only exception is the section-level `> Why ...` blockquote described in Step 3, and only for an approved new section.
- Do NOT hard-code a specific feature name or project-specific identifier — keep the rule general and portable across projects.
- Do NOT touch any file outside `${CLAUDE_PROJECT_DIR}/.claude/rules/`.
- Do NOT delete, rewrite, or reorganize (move between sections, open new sections, or open new files) existing content as part of the new addition unless the user explicitly approved it.

## When to Ask Instead of Acting

- The target file is ambiguous.
- The target section is ambiguous.
- The new rule contradicts an existing rule.
- The wording the user gave is too vague to compress without losing meaning.
- The chosen rule file would become too long or mix unrelated subjects — propose a reorganization (move between sections, new section, or new rule file) and stop.

Ask one focused question, then stop.
