---
paths:
  - "*/splunk_audit/**/*"
---

# splunk_audit/ — Shared-Root Standards

> Standalone Splunk audit-pull tool. Independent of every service's `src/` — reads the shared root's `.env` (`SPLUNK_MONITOR_URL`, `SPLUNK_MONITOR_TOKEN`, `SPLUNK_INDEX`), own output folder, does **not** go through `SplunkRepository`.

## Purpose
Pull logs from Splunk with an arbitrary SPL query and write them, timestamped, into a local `audit_log/` folder. Never overwrites previous pulls.

## Touch / Do NOT touch

| File | Status |
|---|---|
| `run_audit.py` | ✅ **Edit this.** Set `SPL_FILTER` to the filter you want (index is prepended from the shared root's `.env`), then run. |
| `splunk_audit_client.py` | ⛔ **FROZEN — do not touch.** Core client. Interface only via `pull_audit_logs(query)`. |
| `audit_log/` | ⛔ Output only. Git-ignored except `.gitkeep`. Created by the client if missing. |

## How to interface
- Only entry point: `pull_audit_logs(query)` in `splunk_audit_client.py`. Pass a full SPL string; get back the written file path.
- `run_audit.py` builds that string as `search index={SPLUNK_INDEX} {SPL_FILTER}` — index from the shared root's `.env`, filter from the file. The index is always forced so you never pull from another index by accident.
- All filtering (sourcetype, `status=ERROR`, time range via `earliest=/latest=`, pipes, `stats`, …) lives **inside `SPL_FILTER`** — the client sends `search` verbatim and passes no separate REST time params.
- Events are nested JSON in `_raw`; filtering on `status`/`process`/`flow_id`/`content` requires `| spath` first (`... | spath | search status=ERROR`). Prefer this over any client-side post-filtering — filtering stays server-side in SPL by design.
- The SPL string MUST start with `search` (or a generating command like `| tstats`).

## Hard rules
- Do NOT add SPL, filters, or time logic to `splunk_audit_client.py` — it stays query-agnostic. All query intent goes in `run_audit.py`.
- Do NOT wire this tool into any service's `src/`, `SplunkRepository`, or any FastAPI layer. It is standalone by design.
- Do NOT change the timestamped, non-overwriting write behavior in `write_audit_file`.
- Output files are disposable and git-ignored — never commit anything under `audit_log/` except `.gitkeep`.
