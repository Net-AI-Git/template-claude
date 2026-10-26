---
name: init-memory
description: Initialize this project's auto-memory directory with a MEMORY.md index and a decisions.md topic file that records cross-cutting decisions — date, what was decided, why, and what was rejected. Refuses to overwrite an existing memory. Use when the user asks to set up, initialize, bootstrap, or seed memory in a project (typical phrasing — "init memory", "set up the memory", "אתחל את הזיכרון"), typically once after copying this `.claude/` directory into a new project.
---

# init-memory

## Purpose
Create the two starting files in this project's auto-memory directory so decisions have somewhere to
go from the first session. Auto memory is on by default and machine-local — the directory exists but
is empty until something writes to it.

## Required Input
- None. The skill resolves everything from the current session.
- If the session's memory instructions do not name a memory directory, ask the user to run `/memory`
  and paste the auto-memory folder path, then stop.

## Procedure

1. Resolve the memory directory from the path the session's own memory instructions name. Use it
   verbatim. Never compute, guess, or hardcode it — a `autoMemoryDirectory` setting at any scope can
   move it, and the default is keyed by the git repository.

2. Check whether `MEMORY.md` exists in that directory.
   - If it does: STOP. List every file already there with its first line, report that memory is
     already initialized, and change nothing.

3. Write `MEMORY.md` — the index. No frontmatter. One line per topic file:

   ```
   # Memory Index

   ## Project
   - [decisions.md](decisions.md) — every cross-cutting decision: date, what was decided, why, what was rejected
   ```

4. Write `decisions.md` in the same directory:

   ```
   ---
   name: decisions
   description: Every cross-cutting decision taken in this project — date, what was decided, why, and what was rejected
   metadata:
     type: project
   ---

   Cross-cutting decisions for this project, newest first. A decision belongs here when it applies
   beyond one file: layout, tooling, process, a rule or a setting.

   **Why:** the reason a decision was taken, and the alternative that lost, exist in no file — the
   repository records only the outcome. Without them the same option gets re-proposed later and the
   same argument is had again.

   **How to apply:** append an entry the moment a decision is taken, before continuing the work.
   Absolute dates only — never "last week". If a later decision reverses an earlier one, add a new
   entry naming the one it reverses; never edit history away.

   ### YYYY-MM-DD — <what was decided, one line>
   **Why:** <the reason it was chosen>
   **Rejected:** <the alternative> — <why it lost>

   ---
   ```

   Write the entry template as a fenced code block inside the file so it is not read as a real entry.

5. Report the absolute path written to, the two filenames, and that auto memory is machine-local —
   nothing created here is committed or shared with anyone who copies this configuration.

## Hard Prohibitions

- Do NOT overwrite, merge into, or delete an existing `MEMORY.md` or any existing topic file.
- Do NOT hardcode an absolute memory path, a user name, or a project directory name.
- Do NOT seed any decision entry. The file ships empty; entries are added as decisions are taken.
- Do NOT create additional topic files beyond `decisions.md`.
- Do NOT write anything outside the resolved memory directory.
- Do NOT record in memory what a file already states — architecture, paths, or conventions already
  written under `.claude/`.

## When to Ask Instead of Acting

- The session's memory instructions name no memory directory.
- The directory holds files but no `MEMORY.md`, so its state is unclear.
- The user asks to initialize memory for a project other than the current session's.

Ask one focused question, then stop.
