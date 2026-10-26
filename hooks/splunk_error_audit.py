"""PostToolUse / PostToolUseFailure hook: after a command that runs code (pytest, python <file>.py, curl/wget to
localhost), pull that run's Splunk ERROR events and add the verdict to Claude's context.

Reads the hook input JSON on stdin, writes a hook-output JSON on stdout. Holds no SPL — the query
is composed by audit_run_errors() in the shared root's splunk_audit/run_audit.py.
"""

import contextlib
import glob
import io
import json
import os
import re
import sys
import time

IDENTIFIER_PATTERN = re.compile(r"['\"]?(flow_id|batch_id|trace_id|run_id)['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]")
PYTHON_FILE_PATTERN = re.compile(r"python\S*\s+(?:-\w+\s+)*\S+\.py\b")
LOCAL_HTTP_PATTERN = re.compile(r"\b(curl|wget)\b.*\b(localhost|127\.0\.0\.1)\b")
WINDOW_GRACE_SECONDS = 30
INDEX_LAG_SECONDS = 5
MAX_REPORTED_EVENTS = 10
MAX_REASON_CHARS = 4000


def is_code_run(command):
    normalized = command.replace("\\", "/")
    return "pytest" in normalized or bool(PYTHON_FILE_PATTERN.search(normalized) or LOCAL_HTTP_PATTERN.search(normalized))


def locate_splunk_audit(root):
    shared_roots = glob.glob(os.path.join(root, "*", "plans"))
    if len(shared_roots) != 1:
        return None
    return os.path.join(os.path.dirname(shared_roots[0]), "splunk_audit")


def find_identifier(hook_input):
    tool_response = hook_input.get("tool_response", {})
    output = f"{tool_response.get('stdout', '')}\n{tool_response.get('stderr', '')}\n{hook_input.get('error', '')}"
    matches = IDENTIFIER_PATTERN.findall(output)
    return matches[-1] if matches else (None, None)


def pull_errors(audit_dir, identifier_key, identifier_value, earliest):
    sys.path.insert(0, audit_dir)
    from run_audit import audit_run_errors
    with contextlib.redirect_stdout(io.StringIO()):
        audit_file_path = audit_run_errors(identifier_key, identifier_value, earliest)
    if audit_file_path is None:
        return None
    return json.loads(open(audit_file_path, encoding="utf-8").read()), audit_file_path


def describe_event(splunk_row):
    event = json.loads(splunk_row.get("_raw", "{}"))
    content = json.dumps(event.get("content"), ensure_ascii=False)
    return f'{splunk_row.get("_time", "")} · {event.get("process", "")} · flow_id={event.get("flow_id", "")}\n    {content}'


def emit(payload):
    print(json.dumps(payload))
    sys.exit(0)


def report(hook_input, system_message, context):
    emit({"systemMessage": system_message,
          "hookSpecificOutput": {"hookEventName": hook_input.get("hook_event_name", "PostToolUse"), "additionalContext": context}})


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if os.environ.get("RULES_REVIEW_RUNNING") or hook_input.get("tool_name") != "Bash":
        sys.exit(0)

    command = hook_input.get("tool_input", {}).get("command", "")
    if not is_code_run(command):
        sys.exit(0)

    root = hook_input.get("cwd") or os.getcwd()
    audit_dir = locate_splunk_audit(root)
    if audit_dir is None:
        emit({"systemMessage": "Splunk error audit skipped — no single shared root matches */plans/."})
    env_path = os.path.join(os.path.dirname(audit_dir), ".env")
    if not os.path.isfile(env_path):
        emit({"systemMessage": f"Splunk error audit skipped — {env_path} is missing. Copy the .env.example beside it and fill it."})

    identifier_key, identifier_value = find_identifier(hook_input)
    earliest = int(time.time() - hook_input.get("duration_ms", 0) / 1000 - WINDOW_GRACE_SECONDS)
    scope = f"{identifier_key}={identifier_value}" if identifier_key else f"the last {int(time.time()) - earliest}s (no run identifier in the output)"
    time.sleep(INDEX_LAG_SECONDS)

    try:
        pulled = pull_errors(audit_dir, identifier_key, identifier_value, earliest)
    except Exception as err:
        emit({"systemMessage": f"Splunk error audit failed for {scope}: {repr(err)}"})

    if pulled is None:
        emit({"systemMessage": f"Splunk error audit returned nothing for {scope} — the pull itself failed, see the console output of splunk_audit."})

    error_events, audit_file_path = pulled
    if not error_events:
        verdict = f"Splunk: 0 ERROR events for {scope}."
        report(hook_input, verdict, verdict)

    reported = "\n".join(describe_event(splunk_row) for splunk_row in error_events[:MAX_REPORTED_EVENTS])
    context = (f"Splunk returned {len(error_events)} ERROR event(s) for {scope} — the run hit a flow that failed.\n"
               f"{reported[:MAX_REASON_CHARS]}\nFull pull: {audit_file_path}")
    report(hook_input, f"Splunk: {len(error_events)} ERROR event(s) for {scope}. Full pull: {audit_file_path}", context)


main()