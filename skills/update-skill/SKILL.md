---
name: update-skill
description: Modify an existing skill under `.claude/skills/<name>/SKILL.md` based on the user's exact request — minimal wording, no inference, no scope creep. Updates every existing mention of the subject inside the skill for consistency. Use when the user asks to change, tighten, relax, rephrase, extend, or remove behavior of an existing skill under `.claude/skills/` (typical phrasing — "update the skill", "change the skill", "the skill should now ...").
---

# update-skill

## Purpose

Apply a skill change requested by the user to a single existing `SKILL.md` under `${CLAUDE_PROJECT_DIR}/.claude/skills/`, updating every mention of the subject inside that skill (description — including its "Use when ..." activation clause —, procedure, prohibitions, ask-instead clauses) so the skill stays internally consistent.

If the targeted skill does not exist → STOP and tell the user to run `create-skill` instead. This skill does not create new skills.

## Required Input

- The target skill name. If missing or ambiguous → list all skills under `${CLAUDE_PROJECT_DIR}/.claude/skills/` and ask, do not pick.
- The change the user wants, in their own words. Example: "the sync-sdd skill must also reject changes to repository CLAUDE.md without explicit approval".

If the wording is too vague to compress without losing meaning → ask one focused question, then stop.

## Procedure

### Step 1 — Locate the target skill
- Confirm exactly one `${CLAUDE_PROJECT_DIR}/.claude/skills/<name>/SKILL.md` matches.
- If no match → STOP and redirect to `create-skill`.
- If multiple plausible matches → ask, do not pick.

### Step 2 — Find every existing mention
- Read the target `SKILL.md` in full.
- List every section/bullet that mentions the subject of the change (description including its "Use when ..." activation clause, procedure step, prohibition, ask-instead clause, examples).

### Step 3 — Decide scope of edits
- For every hit that contradicts or overlaps with the requested change → it MUST be updated for consistency.
- If the subject is absent and the user wants it added → add it in the single most relevant section of the target skill.
- If two sections seem equally relevant → ask, do not pick.

### Step 4 — Write each addition/modification
- Read `${CLAUDE_PROJECT_DIR}/.claude/prompt-authoring.md` first — it holds the writing standard every prompt under `.claude/` follows, and the section structure a `SKILL.md` keeps.
- Use the **fewest words** that convey the change.
- Match the bullet style, indentation, and heading conventions of neighbouring content.
- Keep the front-matter format intact. `name` and `description` always stay; the activation context lives in `description`'s "Use when ..." clause. Update `description` only if the user's change affects the skill's purpose or activation. Add, change, or remove another field — `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `context` + `agent`, `paths`, `argument-hint`, `arguments`, `when_to_use`, `model`, `effort` — only when the user's change requires it.
- Frontmatter constraints are hard platform requirements — a violation silently breaks skill discovery. After editing, the file MUST still satisfy: `---` on line 1 **and a closing `---` line** before the `# <name>` heading; `name` lowercase letters/numbers/hyphens only, ≤ 64 chars, matching the directory, no XML tags, and free of the reserved words `anthropic` / `claude`; `description` non-empty, ≤ 1024 chars, third person, stating what **and** when; body ≤ 500 lines; forward slashes only, never Windows separators or absolute paths, with `${CLAUDE_SKILL_DIR}/<path>` for a bundled file and `${CLAUDE_PROJECT_DIR}/<path>` for anything outside the skill — never `../`; bundled files referenced one level deep; every MCP tool named fully qualified as `ServerName:tool_name`; no time-sensitive wording ("new", "currently", "as of <version>").
- Write generically — never bind the skill to a specific feature name, service, or project. Use placeholders (e.g. `<feature_name>`, `<name>`) and general phrasing so it stays reusable when `.claude/` is copied to another project.
- A change that adds a step which writes a file states the length that file should be, or hands over a template whose shape decides it. A change that adds a step mentioning a subagent states the threshold that justifies one — a sweep too wide to finish in a handful of tool calls. Never a step whose only action is re-checking the skill's own output.
- A known failure mode the user reports belongs in a `## Gotchas` section placed between `## Procedure` and `## Hard Prohibitions` — add the section if the skill has none.
- No examples, no rationale, no preamble — unless the user explicitly asked for them.

### Step 5 — Apply in one pass
- Apply all edits to the single target `SKILL.md` together.
- Touch ONLY the bullets/lines that mention the subject — do not "harmonize" unrelated sections.
- Do NOT touch any other skill.

### Step 6 — Report
Reply in chat with: the file changed, every section touched, and each new/modified bullet verbatim. Nothing else.

## Hard Prohibitions

- Do NOT create a new skill — redirect to `create-skill`.
- Do NOT leave the file with unclosed frontmatter, a `name` that breaks the Step 4 constraints, an empty `description`, or a bare (unqualified) MCP tool name.
- Do NOT modify any skill other than the one named by the user.
- Do NOT extend the change to cover cases the user didn't mention.
- Do NOT add corollaries, exceptions, or "while we're at it" edits.
- Do NOT rephrase unrelated sections.
- Do NOT add explanations or rationale into the skill itself.
- Do NOT hard-code a specific feature name or project-specific identifier — keep the skill general and portable across projects.
- Do NOT create or delete files inside the skill directory beyond editing the existing `SKILL.md`, unless the user explicitly asked for it or the edit would push the body past 500 lines — then split the overflow into a bundled file referenced one level deep.
- Do NOT delete, rewrite, or reorganize (move between sections, open new sections, or open new files) content unrelated to the requested change unless the user explicitly approved it.

## When to Ask Instead of Acting

- The target skill name is missing or matches more than one directory.
- The change contradicts an existing prohibition or procedure step in the same skill.
- The target section inside the skill is ambiguous.
- The wording the user gave is too vague to compress without losing meaning.
- The requested change would make the skill too large or mix unrelated responsibilities — propose a reorganization (move between sections, new section, or splitting into a new skill) and stop.

Ask one focused question, then stop.
