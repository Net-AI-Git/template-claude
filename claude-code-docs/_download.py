import json
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ClaudeCodeDocsOfflineMirror/1.0"
ACCEPT = "text/markdown, text/plain;q=0.9, */*;q=0.1"
WORKERS = 12
RETRIES = 4
TIMEOUT = 60
URL_RE = re.compile(r"https://(?:code|platform)\.claude\.com/docs/[^\s\)\]]+")

INDEXES = {
    "code.claude.com-llms.txt": "https://code.claude.com/docs/llms.txt",
    "code.claude.com-llms-full.txt": "https://code.claude.com/docs/llms-full.txt",
    "platform.claude.com-llms.txt": "https://platform.claude.com/docs/llms.txt",
}

KEEP_API = {
    "/docs/en/api/overview.md",
    "/docs/en/api/beta-headers.md",
    "/docs/en/api/errors.md",
    "/docs/en/api/versioning.md",
    "/docs/en/api/rate-limits.md",
}

CTX = ssl.create_default_context()


def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": ACCEPT})
    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as resp:
                return resp.read(), resp.geturl(), resp.status
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as err:
            last_err = err
            time.sleep(min(8, 1.5 * attempt))
    raise last_err


def normalize_url(raw):
    url = raw.rstrip(".,;")
    if url.endswith(")"):
        url = url[:-1]
    if not url.endswith(".md") and "/_llms/" not in url:
        if "/docs/" in url and not url.rsplit("/", 1)[-1].endswith(".txt"):
            url = url + ".md"
    return url


def local_path(url):
    path = url.split("://", 1)[1]
    return ROOT / path


def should_keep(url):
    if "code.claude.com/docs/_llms/" in url:
        return False
    if not url.endswith(".md"):
        return False
    if "code.claude.com/docs/en/" in url:
        return True
    if "platform.claude.com/docs/en/" not in url:
        return False
    marker = url.split("platform.claude.com", 1)[1]
    if marker.startswith("/docs/en/api/"):
        return marker in KEEP_API
    return True


def looks_like_markdown(data):
    text = data[:800].decode("utf-8", errors="replace").lstrip("\ufeff")
    if text.startswith("<!DOCTYPE html") or text.startswith("<html"):
        return False
    return True


def download_one(url):
    dest = local_path(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    data, final_url, status = fetch_bytes(url)
    if not looks_like_markdown(data):
        raise ValueError(f"not markdown (status={status} final={final_url})")
    dest.write_bytes(data)
    return dest, len(data)


def extract_urls(text):
    found = []
    seen = set()
    for raw in URL_RE.findall(text):
        url = normalize_url(raw)
        if url in seen or not should_keep(url):
            continue
        seen.add(url)
        found.append(url)
    return found


def title_map(text):
    mapping = {}
    for match in re.finditer(r"\[([^\]]+)\]\((https://(?:code|platform)\.claude\.com/docs/[^\s\)]+)\)", text):
        title, url = match.group(1), normalize_url(match.group(2))
        mapping[url] = title
    return mapping


def write_index(code_text, platform_text, results):
    titles = {}
    titles.update(title_map(platform_text))
    titles.update(title_map(code_text))
    ok = {item["url"]: item for item in results if item["ok"]}
    lines = [
        "# Claude Code + Opus 5 docs (offline)",
        "",
        f"Downloaded: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "Sources: https://code.claude.com/docs/en/ and https://platform.claude.com/docs/en/",
        "Official indexes: `_indexes/code.claude.com-llms.txt`, `_indexes/platform.claude.com-llms.txt`",
        "",
        "This folder is a local markdown mirror. Read these files instead of the internet.",
        "",
        "## Start here by topic",
        "",
        "| Topic | Read first | Then |",
        "| --- | --- | --- |",
        "| Claude Code best practices | `code.claude.com/docs/en/best-practices.md` | `common-workflows.md`, `features-overview.md` |",
        "| When to use CLAUDE.md vs skills vs agents vs rules vs hooks | `code.claude.com/docs/en/features-overview.md` | `memory.md`, `skills.md`, `sub-agents.md`, `claude-directory.md` |",
        "| Write skills | `code.claude.com/docs/en/skills.md` | `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md` |",
        "| Write rules / CLAUDE.md | `code.claude.com/docs/en/memory.md` | `claude-directory.md`, `large-codebases.md` |",
        "| Custom agents / subagents | `code.claude.com/docs/en/sub-agents.md` | `agents.md`, `agent-teams.md`, `workflows.md` |",
        "| Code review | `code.claude.com/docs/en/code-review.md` | `ultrareview.md`, `security-guidance.md` |",
        "| VS Code | `code.claude.com/docs/en/vs-code.md` | `platforms.md`, `permission-modes.md` |",
        "| Opus 5 prompting | `platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5.md` | `claude-prompting-best-practices.md`, `models/opus-5/whats-new-opus-5.md` |",
        "| Opus 5 1M context | `platform.claude.com/docs/en/build-with-claude/context-windows.md` | `models/opus-5/overview.md`, `code.claude.com/docs/en/model-config.md` |",
        "| Effort / thinking | `platform.claude.com/docs/en/build-with-claude/effort.md` | `thinking.md`, `code.claude.com/docs/en/advisor.md` |",
        "",
        "## Claude Code pages",
        "",
    ]
    code_urls = sorted(u for u in ok if "code.claude.com" in u)
    for url in code_urls:
        rel = str(local_path(url).relative_to(ROOT)).replace("\\", "/")
        title = titles.get(url, Path(rel).stem.replace("-", " "))
        lines.append(f"- [{title}]({rel})")
    lines.extend(["", "## Anthropic platform pages (Opus 5, prompting, skills, tools)", ""])
    plat_urls = sorted(u for u in ok if "platform.claude.com" in u)
    for url in plat_urls:
        rel = str(local_path(url).relative_to(ROOT)).replace("\\", "/")
        title = titles.get(url, Path(rel).stem.replace("-", " "))
        lines.append(f"- [{title}]({rel})")
    failed = [item for item in results if not item["ok"]]
    if failed:
        lines.extend(["", "## Failed downloads", ""])
        for item in failed:
            lines.append(f"- `{item['url']}` — {item['error']}")
    (ROOT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    idx_dir = ROOT / "_indexes"
    idx_dir.mkdir(parents=True, exist_ok=True)
    saved = {}
    for name, url in INDEXES.items():
        data, _, _ = fetch_bytes(url)
        path = idx_dir / name
        path.write_bytes(data)
        saved[name] = path
        print(f"index {name} {len(data)} bytes")

    code_text = saved["code.claude.com-llms.txt"].read_text(encoding="utf-8", errors="replace")
    platform_text = saved["platform.claude.com-llms.txt"].read_text(encoding="utf-8", errors="replace")
    urls = extract_urls(code_text) + extract_urls(platform_text)
    urls = list(dict.fromkeys(urls))
    print(f"queued {len(urls)} markdown pages")

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(download_one, url): url for url in urls}
        done = 0
        for fut in as_completed(futs):
            url = futs[fut]
            done += 1
            try:
                dest, size = fut.result()
                rel = str(dest.relative_to(ROOT)).replace("\\", "/")
                results.append({"url": url, "path": rel, "bytes": size, "ok": True})
                print(f"ok {done}/{len(urls)} {rel} ({size})")
            except Exception as err:
                results.append({"url": url, "ok": False, "error": repr(err)})
                print(f"fail {done}/{len(urls)} {url} {err!r}")

    ok = sum(1 for item in results if item["ok"])
    fail = [item for item in results if not item["ok"]]
    manifest = {
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "failed": len(fail),
        "pages": results,
    }
    (ROOT / "_indexes" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_index(code_text, platform_text, results)
    print(f"done ok={ok} failed={len(fail)}")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
