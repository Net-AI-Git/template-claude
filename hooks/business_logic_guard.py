"""Stop hook: run the business-logic guard suites, then ask about unguarded new logic.

Reads the hook input JSON on stdin, writes a hook-output JSON on stdout.
"""

import fnmatch
import hashlib
import json
import os
import subprocess
import sys

PRODUCTION_GLOBS = ["*/src/*.py", "*/main.py", "*/run_*.py"]
STATE_FILE = ".claude/.business-logic-asked"
GUARD_DIR = "tests/pytest_business_logic"
NO_TESTS_COLLECTED = 5
ASK_INSTRUCTION = (
    "This turn changed production code with no business-logic guard recorded for it: {files}. "
    "Invoke the preserve-business-logic skill now, starting at its step 3, so the user can name "
    "what must not drift. The skill records the answer either way, so this will not be asked again "
    "for these file versions."
)


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, shell=False)


def changed_files(root):
    status = run(["git", "status", "--porcelain"], root)
    if status.returncode != 0:
        return []
    paths = []
    for line in status.stdout.splitlines():
        entry = line[3:].strip().strip('"')
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        if entry:
            paths.append(entry.replace("\\", "/"))
    return paths


def is_production(path):
    return any(fnmatch.fnmatch(path, glob) for glob in PRODUCTION_GLOBS)


def service_root_of(path):
    if "/src/" in path:
        return path.split("/src/", 1)[0]
    return path.rsplit("/", 1)[0] if "/" in path else None


def file_sha1(root, path):
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return None
    with open(full, "rb") as handle:
        return hashlib.sha1(handle.read()).hexdigest()


def already_asked(root):
    state = os.path.join(root, STATE_FILE)
    if not os.path.isfile(state):
        return set()
    with open(state, encoding="utf-8") as handle:
        return {line.strip() for line in handle if line.strip()}


def interpreter(root, service):
    venv = os.path.join(root, service, ".venv", "Scripts", "python.exe")
    return venv if os.path.isfile(venv) else sys.executable


def run_guard_suite(root, service):
    suite = os.path.join(root, service, GUARD_DIR)
    if not os.path.isdir(suite):
        return None
    result = run([interpreter(root, service), "-m", "pytest", GUARD_DIR, "-q"],
                 os.path.join(root, service))
    if result.returncode in (0, NO_TESTS_COLLECTED):
        return None
    combined = (result.stdout + result.stderr).strip()
    if "No module named pytest" in combined:
        return (f"{service}: pytest is not installed in that service's environment. "
                f"Run `poetry install` from {service} before finishing.")
    return f"{service}: the business-logic guard suite failed.\n{combined[-4000:]}"


def emit(payload):
    print(json.dumps(payload))
    sys.exit(0)


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if os.environ.get("RULES_REVIEW_RUNNING"):
        sys.exit(0)

    root = hook_input.get("cwd") or os.getcwd()
    production = [path for path in changed_files(root) if is_production(path)]
    if not production:
        sys.exit(0)

    services = sorted({service for service in map(service_root_of, production) if service})
    failures = [message for message in (run_guard_suite(root, service) for service in services)
                if message]
    if failures:
        emit({"decision": "block", "reason": "\n\n".join(failures)})

    if hook_input.get("stop_hook_active"):
        sys.exit(0)

    asked = already_asked(root)
    unguarded = [path for path in production
                 if f"{path}\t{file_sha1(root, path)}" not in asked]
    if not unguarded:
        sys.exit(0)

    emit({"hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": ASK_INSTRUCTION.format(files=", ".join(unguarded)),
    }})


main()
