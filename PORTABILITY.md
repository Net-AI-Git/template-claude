# Portability — why this config names no directory

This directory is its own git repository (`migdal-template-claude`). It is cloned into a workspace,
not written for one. Everything under `rules/`, `skills/` and `output-styles/` must produce the same
behaviour in any repository whose services carry a `src/` — with no edit, and no root `CLAUDE.md`
required to interpret it.

Read this before changing anything under `rules/`. It answers *where a path may point*.
[`prompt-authoring.md`](prompt-authoring.md) answers the other half — *how the text itself is
written*: which mechanism holds which instruction, the rule and skill templates, and the Claude
Opus 5 levers. The two do not overlap; every template there assumes the law below.

---

## The law

> **A file in this repository may name only a path relative to a unit root, a basename, or one of its
> own siblings under `.claude/`. Never a top-level directory, and never a placeholder that another
> file resolves.**

The law binds `rules/`, `skills/`, `output-styles/` and `CLAUDE.md` alike — not `rules/` alone. Five
skills carried 17 `<service>` / `<helper>` tokens until 2026-09-16, each with an instruction to "read
the workspace-root `CLAUDE.md` to find the actual directories". That is the coupling this repository
exists to avoid, wearing a different filename.

Nothing in Claude Code resolves a `<placeholder>` — it is inert prose. A ruleset that says
"`<service>/src/conts.py`" and relies on a file outside `.claude/` to explain what `<service>` means
is not isolated; it is coupled through a second document that may not be there.

## The two roots, resolved by structure

Defined once, in [`rules/00-overview.md`](rules/00-overview.md) under **Vocabulary**. The ruleset
resolves its own terms:

| Term | Marker | Never contains |
|---|---|---|
| **service root** | any directory containing `src/` | `docs/`, `plans/` |
| **shared root** | the directory matching `*/plans/`; it also holds `docs/SDD/` and `docs/spec/` | `src/` |

There is exactly one shared root and several service roots. If a locator glob matches zero or more
than one, stop and ask — that is a tree the ruleset was not written for.

Locate a root by its marker, not by memory.

## The line between the two repositories

Two repositories share one working tree, and every file belongs to exactly one of them. The test is
not "is it about Claude" — it is **would this sentence still be true in a different workspace?**

| | **This repository** (`migdal-template-claude`) | **The workspace repository** |
|---|---|---|
| Holds | How to write code here: rules, skills, output styles, the workspace map | The code, and one identity card per service |
| True in another workspace? | Yes, unchanged | No — it describes these services |
| Names a directory? | Never | Freely — it *is* that directory |
| Who edits it | Whoever owns the standard, for every project at once | The team that owns that service |
| Travels by | `git clone` into each project, then `git pull` in `.claude/` | Not at all |

The consequence that matters: **a standard has exactly one home, and that home is here.** If the same
sentence appears in both repositories, the copy in the workspace is the one that is wrong — it will
drift, and `docs/en/memory.md` warns that when two instructions disagree Claude picks one arbitrarily.

## Why there are no `CLAUDE.md` files next to the code

Until 2026-09-16 this workspace carried **27** `CLAUDE.md` files: one per service root, one per layer
under each `src/`, one per shared-root directory. Twenty of them were byte-identical duplicates across
two services, `tests/` existed in three copies, and 118 markdown links pointed from them back into
`.claude/`. Twenty-four were deleted and their content moved into `rules/` as `05-service-shape.md`,
`10`–`17` and `20`–`24`.

Three reasons, in order of weight:

1. **A standard repeated per service is a standard that diverges.** The two services' layer files were
   identical to the byte. Nothing kept them that way.
2. **It is what the mechanism is for.** `docs/en/memory.md` — *"Reach for a path-scoped rule over a
   nested `CLAUDE.md` when the instruction regards a cross-cutting concern or file that appears in
   multiple corners of the codebase."* A rule on `*/src/services/**/*` covers every service that will
   ever exist in the tree; a nested `CLAUDE.md` covers one and must be copied for the next.
3. **Only one of the two can travel.** A file inside a service directory cannot be pulled from this
   repository. The content was outside the portable unit, which is the whole problem.

What the move did **not** buy, so nobody designs around a myth: compaction behaviour is identical.
`docs/en/context-window.md` puts path-scoped rules and nested `CLAUDE.md` in the same row — both
reload only when their trigger file is read again. Neither fires when Claude *writes* a new file. The
manual patch for that is `01-teach-lesson.md` Section 2, and it is why that file stays unscoped.

### The one exception: the service identity card

Each service root keeps a short `CLAUDE.md`. It is the inverse of everything above — deliberately
**not** portable, because it describes one service and nothing else.

| Belongs in the identity card | Belongs in `rules/` |
|---|---|
| What this service does, in one sentence | What every service must do |
| Which shape it is (FastAPI / cron) | What each shape requires |
| Which layers and repositories it actually uses | How to write each layer |
| Commands unique to it | The standard install and run commands |

It carries **no rules**, restates nothing from `rules/`, links to nothing under `.claude/`, and stays
short — the ~30-line ceiling exists so it is still read. The team edits it freely; this repository
never does.

The workspace map lives at [`CLAUDE.md`](CLAUDE.md) in *this* directory, not at the workspace root.
`docs/en/claude-directory.md` supports both locations and recommends this one *"if you prefer to keep
the project root clean"*. A root `CLAUDE.md` existed alongside it until 2026-09-16 and was deleted:
`docs/en/memory.md` says discovered files **concatenate rather than override**, so two maps do not
resolve to one — they both load, and they drift.

## The three isolation devices

Applied in this order of preference:

1. **Unit-relative path** — drop the root segment entirely. `<service>/src/repositories/x.py` →
   `src/repositories/x.py`. Any path in the ruleset written *without* a leading `*/` is relative to a
   service root. This is the default and covers most cases.
2. **Name-free glob** — for anything that must cross a root boundary. `<helper>/docs/spec/` →
   `**/docs/spec/`. Also the only form usable in `paths:` frontmatter.
3. **Structural predicate** — for the rare statement that has to distinguish the roots: *"the shared
   root's `docs/spec/`"*, not a name. Stated once in the Vocabulary block, never re-derived.

A **basename** (`splunk_repository.py`, `Dockerfile`) is the strongest form when the file is unique
by name — it is directory-independent by construction.

## The targeting layer

`paths:` is the only frontmatter field Claude Code defines for a rule
(`docs/en/memory.md` — *"Rules can be scoped to specific files using YAML frontmatter with the
`paths` field"*). Invent no others.

Globs are matched against project-root-relative paths, so `*/src/**/*.py` **already is** the service
root predicate expressed name-free: "one level down, contains `src/`". That is the whole trick — the
targeting layer needs no vocabulary at all.

Current scoping, all name-free:

| File | Loads |
|---|---|
| `00`, `01`, `05-service-shape.md` | no `paths:` — resident every session, re-injected after `/compact` |
| `02-code-layout.md`, `04-error-and-logging.md` | `*/src/*.py`, `*/src/**/*.py`, `*/main.py`, `*/run_*.py` |
| `03-code-quality.md` | the same four, plus `*/tests/**/*.py` |
| `06-container-build.md` | `*/Dockerfile*`, `*/docker-compose.{yaml,yml}`, `*/.dockerignore`, `**/reference/Dockerfile*` |
| `10-src-package.md` | `*/src/*.py` — the package root only, never the layers below it |
| `11`…`14` | `*/src/{services,repositories,routes,schemas}/**/*` |
| `15-data.md` | `*/src/data/**/*`, `*/evaluations/**/*` |
| `16-notebooks.md` | `*/notebooks/**/*`, `*/src/**/*.ipynb` |
| `17-tests.md` | `*/tests/**/*` |
| `20-docs-sdd.md` | `*/docs/SDD/**/*`, `*/docs/spec/**/*`, `*/docs/testing-process/**/*`, `*/docs/splunk.md` |
| `21`…`25` | `*/{plans,postman,splunk_dashboard,splunk_audit,scripts}/**/*` |

`06`'s last entry is deliberately `**/reference/...` and not `.claude/rules/reference/...`: under a
symlink this directory is not at `.claude/rules/`, and a hardcoded install path stops matching.

**Name-freedom and correct targeting are two different properties.** Both `03` and `20` once had only
the first, and both were narrowed on 2026-09-16. `03` was `**/*.py`, which matched this directory's own
`reference/` templates, tooling shipped inside `skills/`, the vendored docs mirror, and any sibling
checkout beside the services — a 100-plus-line rule with a 20-item checklist loading against files it
was never written for. `20` was `*/docs/**`, which reached into a separate git repository the workspace
map declares out of scope. Both were fixed by enumerating unit-relative shapes instead of reaching for
a bare `**`. Breadth is not portability, and a glob that names no directory can still point at the
wrong one.

`10` is the one rule whose narrow form is deliberate: it governs files sitting directly in `src/`, so
`*/src/*.py` is correct and `**/*` there would swallow every layer and duplicate `11`–`17`.

## Enforcement is name-free too

`settings.json` carries the approval gates as `permissions.ask` rules. Every path there is a
`**/`-anchored glob for the same reason the rules are — it must survive a rename:

```
Edit(**/docs/SDD/**)  ·  Edit(**/docs/spec/**)  ·  Edit(**/src/repositories/splunk_repository.py)
Edit(**/Dockerfile*)  ·  Edit(**/requirements.txt)  ·  Edit(**/pyproject.toml)
```

Use `Edit(...)`, never `Write(...)` — `docs/en/permissions.md` states that a `Write(path)` rule is
accepted but never consulted, and warns at startup.

Caveat that does **not** travel: `settings.json` is read from the session's primary working
directory only, and on Windows there is no fall-back to the repository root. Start the session at
the workspace root, or the enforcement layer silently does not load while the rules still do.

## What travels, and what does not

| Travels | Does not |
|---|---|
| The habit, the contracts, the `> Why` paragraphs | Any literal directory name |
| The Splunk event shape and log statuses | The service identity cards — one per service, by design |
| Naming conventions, layer placement | The approval file list (now in `settings.json`) |
| The `paths:` globs, because they are structural | Anything assuming a specific tree depth |
| The workspace map, at `CLAUDE.md` in this directory | A `CLAUDE.md` at the workspace root — deleted, and it must stay deleted |

A shared file that names a specific directory is a shared file that is wrong somewhere.

## What cannot be isolated

Say these out loud rather than pretending they are solved:

- **Negation.** The shared root's true predicate is "has `docs/` and `plans/` and *no* `src/`".
  `paths:` globs have no negation operator. Fallback: a positive marker unique to it (`*/plans/`).
- **Cardinality.** "Exactly one shared root" is a fact about the tree, not something a rule enforces.
  Fallback: the Vocabulary block says to stop and ask when the glob matches zero or many.
- **Depth.** Every glob assumes services sit one level below the project root. A deeper layout breaks
  them, and `paths:` has no ancestor-relative mode.
- **Residency.** A path-scoped rule cannot make itself load. It fires on a *read*; a task that starts
  by *writing* a new file matches nothing, and after `/compact` it is gone until a matching file is
  read again. `01-teach-lesson.md` Section 2 is the manual patch for this, and it is the reason that
  file stays unscoped.

## Reuse across repositories

**A plugin cannot ship rules.** `docs/en/plugins-reference.md` enumerates plugin components — skills,
agents, hooks, MCP servers, LSP servers, monitors — and the manifest has no `rules` field. It is
explicit that *"a `CLAUDE.md` file at the plugin root is not loaded as project context… To ship
instructions that load into Claude's context, put them in a skill."* Converting this ruleset to a
skill would lose `paths:` auto-loading entirely.

**User-level rules (`~/.claude/rules/`) are the wrong home.** They apply to every project on the
machine, and every glob here encodes a `*/src/`, `*/tests/`, `*/plans/` layout — in an unrelated repo
they would fire on coincidentally-shaped directories.

### How this copy is distributed

`.claude` **stays its own repository**, as the opening paragraph describes, and that repository is
cloned directly into `.claude/` in every project it is used in. Updates travel by `git pull` inside
this directory. A change made here reaches the other projects by being pushed and pulled, never
through anything the host project does.

**The host repository ignores this directory entirely.** It records no gitlink, no `.gitmodules` and
no files — `.claude/` belongs in the host's `.gitignore`. A gitlink there would pin a commit nobody
reads: distribution does not run through the host repository, so a host-repo clone was never the path
by which anyone was meant to receive these files. Worse, a gitlink with no `.gitmodules` beside it
hands whoever clones the host an empty `.claude/`, because `git submodule update --init` has no
mapping to read. Verified by `git ls-files -s .claude` returning nothing.

**Never flatten this repository into a host project.** `git rm --cached .claude` untracks the
directory and is correct — but dropping `.claude/.git` and committing the files is not. That makes one
project self-contained and severs every other project from updates: a change made here would no longer
reach them, and the separate history is gone. If a host repository genuinely must carry a pinned
reference, add a `.gitmodules` entry pointing at this repository's remote and keep it a submodule;
that preserves both separate history and cross-project sharing, at the cost of a bump commit in the
host for every change made here.

## Before you commit a change here

- [ ] `grep -rn '<service>\|<helper>' rules/ skills/ output-styles/ CLAUDE.md` returns nothing
- [ ] No literal directory name anywhere in `rules/`, `skills/`, `output-styles/` or `CLAUDE.md`
- [ ] `grep -rn '\.claude/' --include=CLAUDE.md <workspace>` returns nothing outside this directory —
      no service may point back here
- [ ] `find <workspace> -name CLAUDE.md` returns one file per service root plus this directory's, and
      nothing else. A new `CLAUDE.md` under a layer is a standard that escaped `rules/`
- [ ] A standard you added does not also exist in a service identity card
- [ ] Every new `paths:` entry is name-free and depth-correct
- [ ] A new file under `rules/` carries `paths:`, or you meant it to be resident in every session
- [ ] A new or edited rule, skill or output style follows [`prompt-authoring.md`](prompt-authoring.md)
- [ ] Never put a `.md` file under `rules/reference/` — `.md` files there are discovered recursively
      and load as unscoped rules; that directory holds code templates only
- [ ] Verified, not assumed: start a session, `/context` shows which rules loaded, `/permissions`
      shows which gates are live

## Verified by observation, not by documentation

The whole targeting layer rests on one unstated assumption: that `paths:` globs anchor to the
**project root**. They do. Observed 2026-09-16, session started at the workspace root: reading a
service directory's `src/services/<feature>_service.py` loaded `02`, `03` and `04` — so
`*/src/**/*.py` matched a path whose first segment is the service directory, and `*` consumed
exactly one segment. The claim in **The targeting layer** above now has evidence behind it rather
than inference.

Still unspecified — do not design around a guess: what a `paths:` glob anchors to when the session
starts in a *subdirectory*; whether `**` matches zero path segments; whether HTML comments are
stripped from rule files as they are from `CLAUDE.md`.

Prefer the documented `**/*` form over a bare trailing `**`. `docs/en/memory.md`'s pattern table
gives `src/**/*` for "all files under `src/`" and never shows a trailing `**` — a form that is not in
the table is a form nobody promised.
