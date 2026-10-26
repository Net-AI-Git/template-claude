---
paths:
  - "*/src/*.py"
  - "*/src/**/*.py"
  - "*/main.py"
  - "*/run_*.py"
---

# Phase 3 — Error Handling & Splunk Logging (Hardening)

> Code generated → [`02-code-layout.md`](02-code-layout.md) | Validated → [`03-code-quality.md`](03-code-quality.md)
> Repos → [`reference/gpt_feature_name_repository.py`](reference/gpt_feature_name_repository.py)

## SECTION 1: THE SINGLE TRY/EXCEPT PATTERN

> Why exactly one, at the top of each function: every failure then produces exactly one ERROR event in Splunk, at the level that owns the operation, with the full stack trace intact. Nested handlers multiply events for a single fault and swallow the frames that identify where it started — which makes a production trace unreadable.

- Every function MUST have **exactly one** `try/except Exception` block wrapping all core logic.
- No multiple, nested, or try/except inside helpers.
- Structure: STARTING log → try → except (ERROR log) → FINISHED log → return.
- Catch `Exception` broadly — NOT specific types.
- ALL logic that produces the return value MUST live inside `try` — nothing between `except` and FINISHED except the FINISHED log itself.

## SECTION 2: HELPER FUNCTIONS — NO TRY/EXCEPT
- Internal helpers (`parse_llm_response`, `format_payload`, etc.) have NO try/except.
- Errors bubble up to the caller's single top-level try/except.

## SECTION 3: NO SILENT FAILURES

> Why this is broader than `except`: alerting fires on ERROR events, and the job exits `0` either way. Anything that ends without work done and without a signal is therefore invisible — not degraded, invisible. An exception at least produces a stack trace. The dangerous cases produce a clean, green, empty run, and nobody looks at a green run.

- Every `except` MUST log to Splunk with `level="ERROR"`. No `except: pass` or `except: return`.
- Error content MUST include `repr(err)` — it preserves the exception type name, which `str(err)` drops. The full event shape is Section 7.
- Any failure = entire function fails. No partial execution or recovery.
- **An exception is not the only silent failure.** A query that matched nothing, a filter that removed everything, a lookup that found no rows, a loop whose body never ran, a guard that returned early — none of these raise, and all of them end the work. They are covered by this section.
- **A result of nothing is logged with the reason it is nothing.** The FINISHED event must let a reader tell "there was nothing to do" apart from "we failed to find what was there". A count in `content` is usually enough; where the distinction is not visible from a count, say which case it was.
- **Never return a safe default that reads as success without recording that the default was used.** The safe default exists so the flow survives (Section 4) — not so the failure disappears.

## SECTION 4: SERVICE ENTRY FUNCTIONS

> Why entry points absorb their failures: the orchestrator runs several independent features per flow. One feature's exception must cost that feature only — it is already logged as ERROR, so the flow continues and the remaining features still complete.

- Service entry-point methods return safe defaults on error (`[]`, `""`, `{}`, `None`) — NEVER re-raise.
- Single feature failure MUST NOT crash the entire processing flow.

## SECTION 5: SPLUNK LOG STATUSES
- Three statuses exist and no others — `STARTING`, `FINISHED`, `ERROR` — at every layer alike: orchestrator, service, repository. No intermediate statuses.

## SECTION 6: LOG LEVEL POLICY
- `level="INFO"`: for STARTING, FINISHED.
- `level="ERROR"`: for ERROR status only.

## SECTION 7: LOG FORMATTING

> Why the shape is fixed: dashboards and monitor queries parse these events by field. `content=task_data` verbatim keeps every event queryable on the same keys — a cherry-picked dict silently drops the field a future query needs, and manual timestamps disagree with the infrastructure's own.

- `SplunkRepository.log_event(...)` on a single line.
- Never pass `process=` — Splunk logs MUST never contain it.
- No manual `time.time()` or duration calculations — timestamps from infrastructure.
- Pass `task_data` directly as `content` — no cherry-picked dicts or `{**base_ctx}` spreads.
- STARTING/FINISHED: `content=task_data`. ERROR: `content={"error": repr(err), "task_data": task_data}`.

## REFERENCE EXAMPLES

Two shapes cover every function: one that returns nothing, and one that returns a value.

```python
# Returns nothing — orchestrator or service entry point
def perform_main_flow(task_data, flow_id):
    SplunkRepository.log_event(status="STARTING", content=task_data, flow_id=flow_id, level="INFO")
    try:
        matched_feature_codes = task_data.get("matched_feature_codes", [])
        if FEATURE_CODE in matched_feature_codes:
            run_the_feature_action(task_data, flow_id)
    except Exception as err:
        SplunkRepository.log_event(status="ERROR", content={"error": repr(err), "task_data": task_data}, flow_id=flow_id, level="ERROR")
    SplunkRepository.log_event(status="FINISHED", content=task_data, flow_id=flow_id, level="INFO")
    return

# Returns a value — the safe default is assigned before the try, so an error returns it untouched
@staticmethod
def run_feature(task_data, flow_id):
    SplunkRepository.log_event(status="STARTING", content=task_data, flow_id=flow_id, level="INFO")
    feature_result = None
    try:
        response = GptFeatureNameRepository.client.beta.chat.completions.parse(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), seed=151, top_p=1, response_format=FeatureNameResponse, messages=[...])
        feature_result = response.choices[0].message.parsed
    except Exception as err:
        SplunkRepository.log_event(status="ERROR", content={"error": repr(err), "task_data": task_data}, flow_id=flow_id, level="ERROR")
    SplunkRepository.log_event(status="FINISHED", content=task_data, flow_id=flow_id, level="INFO")
    return feature_result
```

## HARDENING CHECKLIST
- [ ] Every function has exactly ONE try/except (catches `Exception`)
- [ ] STARTING before try, FINISHED after try/except, ERROR inside except
- [ ] No silent failures — every except logs with `repr(err)`
- [ ] Empty results are distinguishable from failures in the FINISHED event (Section 3)
- [ ] No safe default returned without a record that it was used (Section 3)
- [ ] Helpers have NO try/except (errors bubble up)
- [ ] Only STARTING/FINISHED/ERROR statuses (no intermediate)
- [ ] INFO for STARTING/FINISHED, ERROR for ERROR
- [ ] Log calls on single line, no manual timestamps
- [ ] `content=task_data` for STARTING/FINISHED — never cherry-picked dicts
- [ ] Service entry functions return safe defaults (don't crash orchestrator)
