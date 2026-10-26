---
name: create-skill
description: Add a brand-new skill under `.claude/skills/<name>/SKILL.md` based on the user's exact request — minimal wording, no inference, no scope creep. If a skill with overlapping purpose already exists, stop and redirect to `update-skill`. Use when the user asks to add, introduce, or define a new skill under `.claude/skills/` (typical phrasing — "add a skill", "create a skill", "new skill for ...").
---

# create-skill

## Purpose

Create a single new skill directory and `SKILL.md` under `${CLAUDE_PROJECT_DIR}/.claude/skills/` that does not already exist. Refuse overlapping additions — those belong to `update-skill`.

## Required Input

- The exact skill purpose the user wants, in their own words.
- A skill name (kebab-case). If missing → derive the shortest accurate name from the user's purpose and confirm it back in one line before writing.

If the purpose is too vague to compress without losing meaning → ask one focused question, then stop.

## Procedure

### Step 1 — Confirm the skill is new
- List every existing skill directory under `${CLAUDE_PROJECT_DIR}/.claude/skills/`.
- Read each existing `SKILL.md` `name` and `description` field.
- If any existing skill's purpose overlaps with the requested one → STOP. Tell the user to run `update-skill` instead. Do not proceed.

### Step 2 — Confirm the skill name and path
- Path: `${CLAUDE_PROJECT_DIR}/.claude/skills/<name>/SKILL.md` — kebab-case `<name>`. The directory name is the command the user types.
- If the name collides with an existing directory → ask, do not pick.

### Step 3 — Write `SKILL.md`
Read `${CLAUDE_PROJECT_DIR}/.claude/prompt-authoring.md` first — it holds the writing standard every prompt under `.claude/` follows. Then use this exact structure, in this order, with the fewest words that convey the skill. Match the tone and bullet style of the neighbouring skills under `${CLAUDE_PROJECT_DIR}/.claude/skills/`.

```
---
name: <name>
description: <what the skill does, in the third person>. Use when <the task context and the user phrasings that activate it>.
---

# <name>

## Purpose
<one short paragraph: the outcome, and the one thing this skill refuses to do>

## Required Input
<bullets — exactly what the user must provide; what to ask for if missing>

## Procedure
<numbered steps — each step is one focused action; the last step says what to report in chat, and nothing else>

## Gotchas
<bullets — only when the skill has a known failure mode: a shape that looks right and is not, a name that differs between two systems, a check that passes for the wrong reason. Omit the section entirely when there is none>

## Hard Prohibitions
<bullets — what the skill must NEVER do, including the files it may not touch>

## When to Ask Instead of Acting
<bullets — ambiguity cases that must trigger a single focused question, then stop>
```

- `description` is the skill's only auto-invocation surface — a trigger specification, not a summary. Third person, key use case first; `description` plus `when_to_use` is truncated at 1536 characters in the skill listing.
- Add a frontmatter field beyond `name` / `description` only when the skill needs it: `when_to_use` (extra trigger phrases, appended to `description`), `disable-model-invocation` (only the user may invoke — for side-effecting workflows whose timing the user must own), `user-invocable` (only Claude may invoke), `allowed-tools` / `disallowed-tools` (tools pre-approved or removed for the invoking turn), `context: fork` + `agent` + `background` (run in an isolated subagent context; `Explore` and `Plan` also skip every `CLAUDE.md`), `paths` (auto-activate only on matching files), `argument-hint` / `arguments` (declare arguments for `$ARGUMENTS` / `$0` / `$name` substitution), `model`, `effort`, `hooks`.
- Write generically — never bind the skill to a specific feature name, service, or project. Use placeholders (e.g. `<feature_name>`, `<name>`) and general phrasing so it stays reusable when `.claude/` is copied to another project.
- Match freedom to fragility: a fragile one-right-way operation gets an exact command or a verbatim template; an open-ended judgement gets direction and room. Over-specifying a judgement produces a worse answer than leaving it open.
- A step that writes a file states the length that file should be, or hands over a template whose shape decides it. Left unsaid, written deliverables run long.
- No self-verification step. A step survives only when it runs something external and objective — a compiler, a test suite, an HTTP call, a schema check. Re-reading its own output is not a step.
- A step that mentions a subagent states the threshold that justifies one: a sweep too wide to finish in a handful of tool calls. Never a subagent to check the skill's own work.
- No examples, no rationale, no preamble — unless the user explicitly asked for them.
- Do NOT add sections the user didn't request. `Gotchas` is omitted, not left empty, when there is nothing to put in it.

### Step 4 — Validate the frontmatter before writing
These are hard platform constraints — a violation silently breaks skill discovery, so check each one:
- The frontmatter opens with `---` on line 1 and **closes with its own `---` line** before the `# <name>` heading. A missing closing delimiter makes the whole file unparseable and the skill never loads.
- `name`: lowercase letters, numbers, and hyphens only; ≤ 64 characters; matches the directory name; contains no XML tags and neither of the reserved words `anthropic` / `claude`.
- `description`: non-empty, ≤ 1024 characters, written in the third person, and states both **what** the skill does and **when** to use it.
- Body ≤ 500 lines, and well under it where possible — the body stays in context across every later turn once invoked, so every line is a recurring cost. Longer content goes in a bundled reference file, referenced one level deep; a bundled file over 100 lines opens with a contents list.
- All paths use forward slashes — never Windows separators or absolute paths. Address a bundled file by a path relative to the skill directory, or `${CLAUDE_SKILL_DIR}/<path>` where it must resolve regardless of the working directory; address a file outside the skill as `${CLAUDE_PROJECT_DIR}/<path>`. Never climb out of the skill directory with `../`.
- Only `name`, `description`, `allowed-tools`, `license`, `compatibility`, and `metadata` survive an upload to claude.ai or the Skills API — any other field makes that upload fail. Use the rest freely when the skill is Claude Code only.
- Every MCP tool is named fully qualified as `ServerName:tool_name` (e.g. `llm-wiki:llm_wiki_status`); a bare tool name will not resolve.
- No time-sensitive wording ("new", "currently", "as of <version>") — it goes stale silently.

### Step 5 — Create in one pass
- Create `${CLAUDE_PROJECT_DIR}/.claude/skills/<name>/SKILL.md`.
- Bundle a supporting file inside the skill directory when reference material, a template, or a script would otherwise push the body past 500 lines, or when the skill must stay self-contained. Link it from `SKILL.md` one level deep, naming what it holds and when to read it, and state whether Claude runs it or reads it. Give a bundled file over 100 lines a table of contents.
- Do NOT bundle a file `SKILL.md` never references.

### Step 6 — Report
Reply in chat with: the new file path, the skill name, and the `description` line verbatim. Nothing else.

## Hard Prohibitions

- Do NOT proceed if an overlapping skill was found in Step 1 — redirect to `update-skill`.
- Do NOT write the file with unclosed frontmatter, a `name` that breaks the Step 4 constraints, an empty `description`, or a bare (unqualified) MCP tool name.
- Do NOT bundle a supporting file `SKILL.md` never references, and do NOT nest a reference more than one level deep from `SKILL.md`.
- Do NOT add sections beyond the structure in Step 3.
- Do NOT write a step whose only action is Claude re-checking its own output, and do NOT tell the skill to delegate without naming the threshold that justifies it.
- Do NOT extend the skill's behavior to cover cases the user didn't mention.
- Do NOT add explanations or rationale into the skill itself.
- Do NOT hard-code a specific feature name or project-specific identifier — keep the skill general and portable across projects.
- Do NOT touch any file outside the new skill's directory.
- Do NOT delete, rewrite, or reorganize (move between sections, open new sections, or open new files) existing content as part of the new addition unless the user explicitly approved it.

## When to Ask Instead of Acting

- The skill name is ambiguous or collides with an existing directory.
- The requested purpose overlaps with an existing skill in a non-trivial way.
- The user's wording is too vague to compress into a `description` (including its "Use when ..." activation clause).
- The activation context cannot be stated unambiguously (multiple unrelated trigger conditions).
- The requested purpose would make the skill too large or mix unrelated responsibilities — propose splitting into multiple skills and stop.

Ask one focused question, then stop.
