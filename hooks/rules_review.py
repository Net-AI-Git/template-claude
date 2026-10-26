import glob
import json
import os
import re
import subprocess
import sys

CLI_GLOB = os.path.expanduser("~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude.exe")
PROTOCOL = ".claude/review-protocol.md"
REVIEW_TIMEOUT = 3600


def resolve_cli():
    candidates = glob.glob(CLI_GLOB)
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: [int(part) for part in re.findall(r"\d+", path)])[-1]


def governed(path):
    if path.endswith(".py"):
        return "/src/" in path or "/tests/" in path or path.endswith("/main.py") or "/run_" in path
    name = path.rsplit("/", 1)[-1]
    return name.startswith("Dockerfile") or name in ("docker-compose.yml", "docker-compose.yaml", ".dockerignore")


def changed_paths():
    porcelain = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    added, modified = [], []
    for line in porcelain.splitlines():
        path = line[3:].strip().replace("\\", "/")
        if not path or not governed(path):
            continue
        (added if line.startswith("??") else modified).append(path)
    return added, modified


def run_review(cli, added, modified):
    scope = ""
    if added:
        scope += "\n\nNEW FILES — every line is in scope. Read each one in full with the Read tool. `git diff` shows nothing for these; do not run it on them:\n" + "\n".join(added)
    if modified:
        scope += "\n\nMODIFIED FILES — only the changed lines are in scope. Get them with `git diff HEAD -- <path>`:\n" + "\n".join(modified)
    prompt = ("You are a read-only ruleset compliance reviewer. Read " + PROTOCOL + " and follow it exactly. "
              "Its Step 1 early-exit is already done for you — the governed files are listed below, so never return ok:true on the grounds that nothing changed."
              + scope
              + "\n\nYou MUST open every file listed above and every rule file its path selects in Step 3 before you answer. "
                "Returning a verdict without having read them is a failure. Output the JSON from the protocol's Step 7 and nothing else — no prose before or after.")
    environment = dict(os.environ, RULES_REVIEW_RUNNING="1")
    completed = subprocess.run([cli, "--bare", "-p", prompt], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=REVIEW_TIMEOUT, env=environment)
    return completed.stdout


def extract_verdict(output):
    text = re.sub(r"^\s*```(?:json)?\s*$", "", output, flags=re.MULTILINE)
    start = text.find("{")
    if start < 0:
        return None
    try:
        verdict, _ = json.JSONDecoder(strict=False).raw_decode(text[start:])
    except ValueError:
        return None
    return verdict if isinstance(verdict, dict) and "ok" in verdict else None


def main():
    if os.environ.get("RULES_REVIEW_RUNNING"):
        return
    cli = resolve_cli()
    if not cli:
        return
    added, modified = changed_paths()
    if not added and not modified:
        return
    verdict = extract_verdict(run_review(cli, added, modified))
    if not verdict or verdict.get("ok"):
        return
    print(json.dumps({"decision": "block", "reason": verdict.get("reason", "Ruleset violations found.")}))


main()
