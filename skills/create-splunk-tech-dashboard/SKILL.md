---
name: create-splunk-tech-dashboard
description: Build a Splunk "tech" dashboard (Simple XML `<form>`) for one microservice or a multi-service pipeline from the `SplunkRepository.log_event` events it already emits — KPIs, per-service tables, error panels, and filter tokens. Enforces the universal structure, SPL idioms, performance pattern, and UX rules for every dashboard XML under the workspace's shared `splunk_dashboard/` directory. Use when the user asks to create, build, generate, edit, review, or export a Splunk technical/prod dashboard XML for a service or pipeline (typical phrasing — "create a splunk tech dashboard", "build the prod dashboard xml", "review the dashboard").
---

# create-splunk-tech-dashboard

## Purpose

Generate or edit a Splunk Simple XML `<form>` dashboard under the shared root's `splunk_dashboard/`. The **shared root** is the single top-level directory matching `*/plans/`; locate it by that marker, never by name. A **service root** is any directory containing `src/`. The dashboard visualizes the STARTING / FINISHED / ERROR events a microservice (or a multi-service pipeline) already writes via `SplunkRepository.log_event(...)`. This skill both **builds** the dashboard from real emitted logs and **enforces** the universal skeleton, SPL idioms, performance pattern, and UX conventions on every create or edit. It reads existing logs only — it never adds instrumentation, endpoints, or alerts.

## Required Input

- Target file path (existing or new) under the shared root's `splunk_dashboard/`. If missing → default to `<shared root>/splunk_dashboard/<dashboard_name>.xml` and confirm.
- The target microservice(s) and their Splunk `sourcetype`(s). If missing → ask; do not guess sourcetype names.
- The Splunk `index`. If missing → ask.
- Which `content.*` fields carry the KPIs the user wants surfaced. If unknown → derive them by reading the service's `SplunkRepository.log_event(...)` call sites; do not invent field paths.
- The dashboard's purpose (one line). If missing → ask once and stop.

If the user's intent is too vague to pick even one KPI → ask one focused question, then stop.

## Procedure

### Step 1 — Discover the log shape (never assume field paths)
- Read the target service's repositories/services to list every `SplunkRepository.log_event(...)` call: its `status` and every key inside `content`.
- For a single service, read the call sites directly. For a pipeline spanning more services than you can sweep in a handful of tool calls, fan the discovery out with the `Agent` tool (`Explore` subagent) — one subagent per microservice — each returning every `SplunkRepository.log_event(...)` call site it found (`status` + `content.*` keys); consolidate the field inventory yourself. Efficiency only — every field the dashboard reads MUST still trace to a real call site.
- Confirm the `index` + `sourcetype` per service. Every field the dashboard reads MUST correspond to a field the code actually logs.

### Step 2 — Structural universals (MUST)
- Root element: `<form version="1.1" theme="light">` (never `<dashboard>`).
- First child after `<label>` and one-line `<description>`: an `<fieldset submitButton="false">` containing the **time picker as the FIRST input**, placed in the top row of the form.
- The time picker MUST be a single `type="time"` token named `global_time` with default `earliest=-24h@h` and `latest=now`. Every panel search binds to it via `<earliest>$global_time.earliest$</earliest>` and `<latest>$global_time.latest$</latest>` — no panel uses hardcoded time ranges.
- Every dashboard MUST auto-refresh: add `<refresh>5s</refresh>` and `<refreshType>delay</refreshType>` at the form level.
- All searches MUST use `index=<confirmed_index>` with a **specific** `sourcetype` — never `index=*`, never `sourcetype=*`.
- All searches MUST extract via `spath input=event`.
- All searches MUST filter `status IN (STARTING, FINISHED, ERROR)` only.
- Every stats/chart panel MUST set `drilldown="none"` unless the user explicitly requests drilldown.

### Step 3 — Plan panels (closed menu, ordered)
Include only the sections the emitted logs actually support, in this order:
1. Overview KPIs (single-value panels)
2. Per-Microservice Summary (tables)
3. Domain feature panels (charts/tables)
4. Errors (by service / timeline / by function / full detail table)
5. Optional Health Check panel

Each section is separated by an `<html><h2 style="text-align:center; border-top:2px solid #ccc;">…</h2></html>` banner row — never use inline panel titles for sections.

### Step 4 — Shared base search (MUST when 2+ panels share a time/index scope)
- Define a base search once with `<search id="base_*">` and have panels post-process via `<search base="base_*">`.
- Never re-scan the index per panel.

### Step 5 — Recurring filter inputs (SHOULD when relevant)
- Text inputs with default `*` for correlation ids the logs actually carry (e.g. `flow_filter`, `batch_filter`, `<domain_id>_filter`).
- Combine each token with the wildcard filter idiom: `where ("$tok$"="*" OR field="$tok$")`.

### Step 6 — SPL idioms (MUST when applicable)
- Latency per flow: `stats min(_time) as t_start max(_time) as t_end by flow_id | eval latency_sec=t_end-t_start | where latency_sec>0`.
- Multi-shape field extraction: extract each shape with its own `spath ... output=_a`, then `eval field=coalesce(_a,_b,...,"unknown")`.
- Error rollup per flow: `eval err=if(status="ERROR",1,0) | stats max(err) as is_err by flow_id`.

### Step 7 — Visual conventions (MUST)
- KPI / status color palette:
  - Green `#53a051` = healthy / FINISHED
  - Yellow `#f8be34` = warning / partial
  - Red `#dc4e41` = ERROR
  - Blue `#5379af` = neutral metric
- Single-value KPIs use `colorMode=block`, `useColors=1`, `rangeColors`, `rangeValues`. Reverse the palette only where higher-is-better (e.g. success rate) — document it.

### Step 8 — Color threshold reference (only if colored KPIs exist)
- If the dashboard contains any colored KPI, write `<shared root>/splunk_dashboard/<dashboard_name>_colors.md`: palette table + per-panel `rangeValues` meaning.

### Step 9 — Verify + report
- Confirm the XML is well-formed (all `<`, `>`, `&` inside SPL escaped as `&lt;`, `&gt;`, `&amp;`).
- Read the final XML and confirm every MUST in Steps 2, 4, 6, 7 is satisfied.
- Report: the file path(s) created, the sections included, and any KPI the user requested that the logs could NOT support (list the missing `content.*` field).
- If any MUST cannot be satisfied (e.g. the user explicitly refuses one), STOP and surface the conflict before writing.

## Hard Prohibitions

- Do NOT invent `sourcetype` or `content.*` field names — every one MUST trace to a real `SplunkRepository.log_event(...)` call or be confirmed by the user.
- Do NOT pass `process=` anywhere, and do NOT search on `process` in SPL — logs must never contain it.
- Do NOT use `index=*` or `sourcetype=*`.
- Do NOT hardcode time ranges in any panel — all panels bind to the `global_time` token.
- Do NOT place the time picker anywhere other than the top row.
- Do NOT omit `<refresh>5s</refresh>` + `<refreshType>delay</refreshType>` — auto-refresh is mandatory on every dashboard.
- Do NOT introduce drilldowns unless the user explicitly asked.
- Do NOT use colors outside the palette in Step 7 for status indicators.
- Do NOT skip the shared base search when 2+ panels share scope.
- Do NOT add panels, inputs, sections, or SPL idioms the user did not request.
- Do NOT modify any application code — this skill reads logs and writes dashboard files only.
- Do NOT edit any service's `src/repositories/splunk_repository.py`.
- Do NOT add instrumentation, `/monitor` endpoints, probes, or Splunk alerts.
- Do NOT leave raw `<`, `>`, `&` inside `<query>` SPL — escape them so the XML stays valid.
- Do NOT write the dashboard outside the shared root's `splunk_dashboard/` unless the user specifies a path.

## When to Ask Instead of Acting

- The dashboard's purpose, target `index`, or any `sourcetype` is unclear.
- A requested KPI has no backing field in the emitted logs (state which field is missing).
- The scope is unclear: single service vs. multi-service pipeline (they produce different Overview/Summary sections).
- The output file name/location is unspecified and no default fits.
- A panel genuinely needs a time range different from the top-row `global_time` picker — confirm before deviating.
- The user requests a color, refresh interval, or layout that conflicts with the MUSTs above.
- The dashboard has only one panel and a base search would be unnecessary — confirm before adding it anyway.

Ask one focused question, then stop.
