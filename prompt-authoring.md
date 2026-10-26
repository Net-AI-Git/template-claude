# Prompt Authoring — the writing standard for everything under `.claude/`

> This file is the single source of truth for **how** a rule, a skill, or an output style is written
> here. It does not say what any of them must contain — that is each file's own business.
>
> It is not loaded automatically. `create-rule`, `update-rule`, `create-skill` and `update-skill`
> point at it; read it before authoring or editing any prompt in this directory.
>
> Portability is decided in [`PORTABILITY.md`](PORTABILITY.md) and is not restated here. Every
> template below assumes it.

## Contents

- [Pick the mechanism first](#pick-the-mechanism-first)
- [The five laws](#the-five-laws)
- [Rule file template](#rule-file-template)
- [Skill file template](#skill-file-template)
- [Writing for Claude Opus 5](#writing-for-claude-opus-5)
- [Frontmatter — hard platform constraints](#frontmatter--hard-platform-constraints)
- [Anti-patterns](#anti-patterns)

---

## Pick the mechanism first

Most bad prompts here are good prompts in the wrong file. Decide by **when the text must be in
context**, not by what it is about.

| The text is… | Goes in | Loads |
|---|---|---|
| A fact true of every session — the workspace map, the two roots | [`CLAUDE.md`](CLAUDE.md) | Every session, re-read after `/compact` |
| A constraint on code in one kind of file | a `paths:`-scoped file under [`rules/`](rules/) | When a matching file is **read** — never when one is written |
| A constraint that must be resident even while writing a new file | an unscoped file under [`rules/`](rules/) (`00`, `01`, `05`) | Every session |
| A procedure with steps, gates and a report | a skill under [`skills/`](skills/) | Name + description every session; body on invoke |
| How Claude talks, asks and scopes its answers | [`output-styles/AI-Engineer.md`](output-styles/AI-Engineer.md) | System prompt, never compacted |
| Something that must happen whether or not Claude decides to | a hook in [`settings.json`](settings.json) | On the lifecycle event |
| Something that must never happen | `permissions.deny` / `permissions.ask` in [`settings.json`](settings.json) | Enforced by the client |

Three consequences worth stating out loud:

- **A `paths:` rule cannot make itself load.** It fires on a read. A task that starts by *writing* a
  new file matches nothing, and after `/compact` it is gone until a matching file is read again.
  [`rules/01-teach-lesson.md`](rules/01-teach-lesson.md) Section 2 is the manual patch, and it is why
  that file stays unscoped.
- **A skill's body persists once invoked.** It enters the conversation as one message and stays
  across later turns; Claude Code does not re-read the file. Write standing instructions, not
  one-time steps — and treat every line as a recurring token cost.
- **An instruction is never a guardrail.** "Never do X" in a rule is followed most of the time. If X
  must not happen, it belongs in `permissions.deny` or a `PreToolUse` hook.

## The five laws

**1. Only write what Claude does not already know.** Claude can code and can read this repo. A
sentence that restates the default costs tokens and buys nothing. The highest-signal content is
always the part that pushes against the default — which is exactly what the `> Why` blockquotes and
the `Hard Prohibitions` sections are for.

**2. State the constraint, then the reason it exists.** A rule with its motivation generalises to
cases the rule never listed; a bare prohibition does not. That is what the `> Why …` blockquote under
a section heading is for — one per section, never per bullet.

**3. Say what to do, not only what not to do.** `Do NOT use a class` is weaker than `Module-level
functions, no class`. Keep the negative form for the `Hard Prohibitions` block, where it is the
point.

**4. Match freedom to fragility.** A fragile, one-right-way operation gets an exact command or a
verbatim template. An open-ended judgement gets direction and room. Over-specifying a judgement
railroads Claude into a worse answer than it would have found alone.

**5. Be consistent in wording.** One term per concept, everywhere. Mixing *entry point* / *entry
function* / `run_*`, or *service root* / *microservice directory*, makes Claude resolve a synonym
before it can follow the instruction.

## Rule file template

A new file under `rules/` needs approval first (`create-rule` Step 2). When one is approved:

```markdown
---
paths:
  - "*/src/<layer>/**/*"
---

# <Directory or phase name> — <Layer / Phase> Standards

> One line placing this file in the chain: what came before, what comes next.
> **Scope:** what this file decides — and the one sentence naming what it deliberately leaves to
> another file, so the two never restate each other.

## SECTION 1: <THE CONSTRAINT, NAMED>

> Why: the failure this section prevents, in concrete terms — what breaks, for whom, and when.

- <one requirement per bullet, imperative, no rationale inside the bullet>
- <a **BAD:** / **GOOD:** pair only where the wording alone is ambiguous>

## Forbidden in this directory

- <the negative form of the same constraints, for the reviewer>

## REVIEW CHECKLIST

- [ ] <one checkable line per requirement, each naming its section>
```

Rules for the rules:

- `paths:` is the only frontmatter field Claude Code defines for a rule. Invent no others.
- Every glob is name-free and anchored one level below the project root (`*/src/**/*.py`). Breadth is
  not portability — a bare `**/*.py` also matches this directory's own templates and any sibling
  checkout.
- A file with no `paths:` is resident in every session. That is a deliberate, expensive choice; make
  it only for an index that must survive a task which starts by writing.
- Target under 120 lines. Past that, the file is doing two jobs — split it, or move the overflow into
  a code template under `rules/reference/`.
- **Never put a `.md` file under `rules/reference/`.** Files there are discovered recursively and load
  as unscoped rules. That directory holds code templates only (`.py`, `Dockerfile`).
- Keep the canonical code examples inline in the rule that owns them. They are the highest-signal
  part of the file and the reason it exists; extracting them to save a few hundred tokens trades the
  example away for a Read that may not happen.

## Skill file template

```markdown
---
name: <kebab-case, matches the directory name>
description: <what it does, in the third person>. Use when <the task context and the phrasings that
  should activate it>.
---

# <name>

## Purpose
<one short paragraph: the outcome, and the one thing this skill refuses to do>

## Required Input
- <exactly what the user must supply, and what to ask for when it is missing>

## Procedure
### Step 1 — <focused action>
- <what to do>
### Step N — Report
<what to say in chat when done, and nothing else>

## Gotchas
- <the failure Claude actually hits when running this skill, and the way past it>

## Hard Prohibitions
- <what the skill must NEVER do>

## When to Ask Instead of Acting
- <the ambiguity cases that must trigger one focused question, then stop>
```

- **`description` is the only auto-invocation surface.** It is not a summary — it is a trigger
  specification. Put the key use case first: `description` plus `when_to_use` is truncated at 1,536
  characters in the skill listing. Third person always; a first- or second-person description
  ("I can help you…", "You can use this to…") breaks discovery.
- Put extra trigger phrasings in `when_to_use` rather than growing `description`.
- **`Gotchas` is the highest-value section.** Grow it from failures observed in real runs — a shape
  that looks right and is not, a field that is named two different things, a check that passes for
  the wrong reason. A skill with no gotchas is usually a skill that restates the default.
- **Progressive disclosure.** Body under 500 lines, and well under it where possible. Long templates,
  verbatim code shapes and API references move into a bundled file in the skill directory, linked
  from `SKILL.md` **one level deep** and named for what it holds. Say whether Claude *runs* it
  ("Run `scripts/x.py`") or *reads* it ("See `reference/x.md` for the shape").
- A bundled file over 100 lines opens with a contents list, so a partial read still shows its scope.
- Never bundle a file `SKILL.md` does not reference.
- Give `Step 1` a cheap early exit where one exists. Most invocations of a guard-style skill should
  end in the first step.

## Writing for Claude Opus 5

This repository targets Claude Opus 5 only. Five of its behaviours change what a prompt here should
say, and two of them mean **deleting** text rather than adding it.

**Delete: self-verification scaffolding.** Opus 5 verifies its own work without being told. "Add a
final verification step", "double-check your answer", "use a subagent to confirm" compound with that
and produce over-verification — more tokens, no more quality. A verification step survives here only
when it runs something external and objective: a compiler, a test suite, an HTTP call, an XML
well-formedness check. Re-reading its own output is not a step.

**Delete: anti-laziness prompting.** `CRITICAL: you MUST…` on a tool or skill that under-triggered on
an older model now over-triggers. Plain `Use X when…` is the correct strength.

**Add: a delegation threshold wherever a skill mentions subagents.** Opus 5 delegates more readily
than prior models, and delegation multiplies cost on small tasks. A skill that fans out says so
conditionally — *when* the sweep is wide enough to justify it — and never delegates verification of
its own work. Independent of cost: a subagent summary does not satisfy a read list, because `Explore`
and `Plan` load neither `CLAUDE.md` nor this ruleset
([`rules/01-teach-lesson.md`](rules/01-teach-lesson.md) Section 3).

**Add: length calibration on anything written to disk.** Opus 5's files — reports, markdown
documents, summaries — run longer than prior models'. Every skill that writes a document states the
length it should be, or hands over a template whose shape decides it.

**Add: narration cadence for long agentic runs.** Opus 5 narrates readily between tool calls. Where
that matters, the shape of the updates is described positively — a positive example of the cadence
you want beats a list of things not to say.

**Scope.** Opus 5 can widen a task on its own judgement. Every skill here already ends with
`Hard Prohibitions`; the one that matters most is the one naming the files the skill may not touch.

## Frontmatter — hard platform constraints

A violation here does not warn — the skill silently never loads. Check each before writing.

- `---` on line 1, and **its own closing `---`** before the first heading.
- `name`: lowercase letters, numbers and hyphens only; ≤ 64 characters; matches the directory name;
  no XML tags; never contains the reserved words `anthropic` or `claude`.
- `description`: non-empty, ≤ 1024 characters, third person, states both what **and** when.
- Body ≤ 500 lines.
- Forward slashes in every path. Never a Windows separator, never an absolute path, never `../` out of
  the skill directory. Use `${CLAUDE_SKILL_DIR}/<path>` for a bundled file that must resolve from any
  working directory, and `${CLAUDE_PROJECT_DIR}/<path>` for anything outside the skill.
- Every MCP tool named fully qualified as `ServerName:tool_name`. A bare name does not resolve.
- Optional fields, used only when the skill needs them: `when_to_use`, `disable-model-invocation`,
  `user-invocable`, `allowed-tools`, `disallowed-tools`, `context: fork` + `agent`, `background`,
  `paths`, `argument-hint`, `arguments`, `model`, `effort`, `hooks`.
- Only `name`, `description`, `allowed-tools`, `license`, `compatibility` and `metadata` survive an
  upload to claude.ai or the Skills API. Any other field makes that upload fail outright — use the
  rest freely while the skill is Claude Code only.

## Anti-patterns

- **A procedure in a rule file.** Rules are constraints. Steps, gates and reports are a skill.
- **An unscoped rule that only applies to one directory.** Mechanically identical to putting it in
  `CLAUDE.md`: always loaded, always paid for.
- **"Every time X, always do Y" as prose.** If it must happen reliably, it is a hook.
- **A menu of options.** Give one default and one named escape hatch. Three alternatives with no
  recommendation is a decision handed back to the reader.
- **Time-sensitive wording.** "new", "currently", "as of <version>" goes stale silently. Put
  superseded material under an explicit old-patterns heading instead.
- **A nested reference.** `SKILL.md` → `a.md` → `b.md` gets partially read. Everything links directly
  from `SKILL.md`.
- **Two files stating the same standard.** When they disagree, Claude picks one arbitrarily. One
  home per standard; everywhere else links to it.
