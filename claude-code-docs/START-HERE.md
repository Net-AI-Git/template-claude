# מפת קריאה — Claude Code + Opus 5 (offline)

קובץ זה הוא האינדקס. **אל תנחש.** קרא את הקבצים המקומיים ברשימה שלמטה לפי סוג השאלה, ואז הפנה לקובץ המדויק.

מקורות שהורדו:

- כל דוקומנטציית Claude Code באנגלית מ-[code.claude.com/docs/en](https://code.claude.com/docs/en/)
- דוקומנטציית הפלטפורמה (Opus 5, prompting, skills, tools, context 1M) מ-[platform.claude.com/docs/en](https://platform.claude.com/docs/en/)
- מאמרי Anthropic הרשמיים שמקושרים מהדוקומנטציה

רענון מהאינטרנט (כשיש רשת): `python claude-code-docs/_download.py`

קטלוג מלא של כל עמודי הדוקס: [`INDEX.md`](INDEX.md)

---

## 1. Skills — איך כותבים נכון

1. `code.claude.com/docs/en/skills.md` — מבנה תיקייה, `SKILL.md`, frontmatter, progressive disclosure, bundled skills כולל `/code-review`
2. `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md` — חוקי כתיבה: description, גודל גוף, קבצי reference, scripts
3. `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md` + `quickstart.md`
4. `claude.com/blog/lessons-from-building-claude-code-how-we-use-skills.md` — איך Anthropic עצמם כותבים skills (כולל review skills)
5. `claude.com/blog/skills-explained.md` — Skill מול prompt / MCP / subagent
6. `claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills.md`

**מתי skill:** פרוצדורה חוזרת, playbook, checklist, ידע שנטען רק כשצריך. לא עובדה שחייבת להיות בכל סשן.

## 2. Rules / CLAUDE.md — איך כותבים נכון

1. `code.claude.com/docs/en/memory.md` — CLAUDE.md, `.claude/rules/`, path-scoped rules, auto memory
2. `code.claude.com/docs/en/claude-directory.md` — מה חי ב-`.claude/`
3. `code.claude.com/docs/en/features-overview.md` — מתי CLAUDE.md מול skill מול rule מול hook מול subagent
4. `claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more.md` — טבלת החלטה + דוגמת YAML ל-`paths`
5. `claude.com/blog/using-claude-md-files.md`
6. `code.claude.com/docs/en/large-codebases.md` — CLAUDE.md מקונן במונורפו

**מתי rule:** אילוץ/קונבנציה לקבצים מסוימים (`paths:`). **מתי CLAUDE.md:** עובדות תמיד-רלוונטיות, פחות מ-~200 שורות. **"Never do X"** לא שייך ל-CLAUDE.md — זה hook / permissions.

## 3. Agents / subagents — מתי שמים

1. `code.claude.com/docs/en/sub-agents.md` — frontmatter, isolation, tools, model, skills
2. `code.claude.com/docs/en/agents.md` — השוואת דרכי מקביליות
3. `code.claude.com/docs/en/agent-teams.md` + `workflows.md` + `worktrees.md`
4. `claude.com/blog/subagents-in-claude-code.md`
5. `code.claude.com/docs/en/agent-sdk/subagents.md` — caps ל-Opus 5 (`MAX_SUBAGENT_SPAWN_DEPTH`, concurrency)

**מתי agent:** עבודה מבודדת / מקבילית שאין צורך בתוצאות הביניים בחלון הראשי. **מתי skill:** אותו playbook בתוך השיחה הראשית כדי לראות ולנווט כל שלב.

## 4. Code review — הדרך הנכונה ב-VS Code / Claude Code

1. `code.claude.com/docs/en/code-review.md` — PR review מנוהל + `/code-review` מקומי + `REVIEW.md` / `CLAUDE.md`
2. `code.claude.com/docs/en/ultrareview.md` — `/code-review ultra` בענן
3. `code.claude.com/docs/en/commands.md` — `/code-review`, `/review`, `/simplify`, `/security-review`
4. `code.claude.com/docs/en/vs-code.md` — הרחבת VS Code: diffs, plan review, shortcuts
5. `code.claude.com/docs/en/security-guidance.md` + `claude-security.md`
6. `code.claude.com/docs/en/best-practices.md` — adversarial review step
7. `claude.com/blog/lessons-from-building-claude-code-how-we-use-skills.md` — `adversarial-review` כ-skill

**ב-VS Code:** `/code-review` על ה-diff המקומי; `--fix` ליישום; `--comment` לפוסט על PR. לעומק: `ultra`. ל-CI מנוהל: עמוד `code-review.md`. ל-CI עצמי: `github-actions.md` / `gitlab-ci-cd.md`.

**Opus 5 ב-review:** לבקש לדווח הכל ולסנן בנפרד. אל תכתוב "only high-severity" אם רוצים כיסוי. ראה prompting-opus-5.

## 5. Best practices כלליים ל-Claude Code

1. `code.claude.com/docs/en/best-practices.md`
2. `code.claude.com/docs/en/common-workflows.md`
3. `code.claude.com/docs/en/how-claude-code-works.md`
4. `code.claude.com/docs/en/context-window.md`
5. `claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start.md`
6. `claude.com/blog/maximizing-the-value-of-your-claude-code-sessions.md`
7. `www.anthropic.com/engineering/claude-code-best-practices.md`

## 6. Opus 5 — איך לדבר עם המודל, ובפרט 1M

1. `platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5.md` — **העמוד הספציפי ל-Opus 5**
2. `platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md` — טכניקות כלליות (XML, examples, long context)
3. `platform.claude.com/docs/en/models/opus-5/overview.md` + `whats-new-opus-5.md` + `migration-guide.md`
4. `platform.claude.com/docs/en/build-with-claude/context-windows.md` — 1M הוא ברירת המחדל וגם המקסימום ב-Opus 5, בלי beta header
5. `code.claude.com/docs/en/model-config.md` — ב-Claude Code: `opus[1m]`, `opusplan[1m]`, `/effort`, `CLAUDE_CODE_DISABLE_1M_CONTEXT`
6. `platform.claude.com/docs/en/build-with-claude/effort.md` + `thinking.md`
7. `claude.com/blog/claude-model-and-effort-level-in-claude-code.md`
8. `www.anthropic.com/engineering/effective-context-engineering-for-ai-agents.md`
9. `platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-5.md`

נקודות קשיחות מ-Opus 5 prompting (לא לדלג):

- לתת את כל המפרט מראש ולתת לו לרוץ; לא stub-ים
- effort ברירת מחדל `high`; `low`/`medium` חזקים למהירות; `xhigh`/`max` לעבודה קשה
- לא להוסיף "verify again" / "double-check" — הוא כבר עושה verification לבד
- להגביל spawn של subagents; לא להשתמש בהם לאימות עצמי
- לקצר תשובות במפורש אם רוצים קצר — effort לא מקצר את הטקסט הנראה
- thinking כבוי רק ב-effort `high` ומטה; עדיף thinking דולק + effort נמוך
- 1M: לשים מסמכים ארוכים למעלה, XML tags, לצטט לפני ניתוח — ב-`claude-prompting-best-practices.md`

## 7. VS Code

1. `code.claude.com/docs/en/vs-code.md`
2. `code.claude.com/docs/en/platforms.md`
3. `code.claude.com/docs/en/permission-modes.md`
4. `code.claude.com/docs/en/interactive-mode.md` + `keybindings.md`

## 8. Hooks / הרשאות / מבנה `.claude`

- Hooks: `code.claude.com/docs/en/hooks-guide.md`, `hooks.md`, `claude.com/blog/how-to-configure-hooks.md`
- Permissions: `permissions.md`, `permission-modes.md`, `sandboxing.md`
- Settings: `settings.md`, `settings-reference.md`

## כלל הפניה

כשנשאלת שאלה:

1. זהה את הנושא לפי הסעיפים למעלה.
2. קרא את **"קרא ראשון"** של אותו סעיף.
3. אם חסר מבנה/שדה/פקודה — עבור לקובץ ה-Then.
4. אל תסתמך על זיכרון מול הדוקס המקומיים; הם המקור.
