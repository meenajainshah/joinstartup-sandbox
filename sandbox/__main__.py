#!/usr/bin/env python3
"""joinstartup sandbox CLI (standard library only).

Commands:
  python -m sandbox login <token>
  python -m sandbox status
  python -m sandbox start
  python -m sandbox env
  python -m sandbox grade predictions.jsonl
  python -m sandbox submit --repo URL --video URL --note URL
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "sandbox" / "config.json").read_text())
TOKEN_FILE = ROOT / ".sandbox" / "token"
TOKEN_PREFIX = "sbx_"


def read_token() -> str:
    env = os.environ.get("SANDBOX_TOKEN", "").strip()
    if env:
        return env
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    sys.exit("Not logged in. Run: python -m sandbox login <your token>")


def call(method: str, path: str, body=None, token: str | None = None) -> dict:
    url = CONFIG["api_base"].rstrip("/") + "/sandbox-api" + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token or read_token()}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read())
        except Exception:
            payload = {"error": f"http_{e.code}"}
        message = payload.get("message") or payload.get("error")
        extra = payload.get("errors")
        if extra:
            message = f"{message}\n  " + "\n  ".join(str(x) for x in extra)
        sys.exit(f"Error {e.code}: {message}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def git(*args: str) -> str | None:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def cmd_login(args):
    token = args.token.strip()
    if not token.startswith(TOKEN_PREFIX) or len(token) != len(TOKEN_PREFIX) + 48:
        sys.exit("That doesn't look like a sandbox token (it starts with sbx_).")
    status = call("GET", "/status", token=token)
    TOKEN_FILE.parent.mkdir(exist_ok=True)
    TOKEN_FILE.write_text(token)
    os.chmod(TOKEN_FILE, 0o600)
    print(f"Logged in. Brief: {status['brief']['title']} · status: {status['status']}")


def cmd_status(_args):
    s = call("GET", "/status")
    print(json.dumps(s, indent=2, default=str))


def cmd_start(_args):
    r = call("POST", "/start")
    print(f"Started. Deadline: {r['deadline_at']}")


def cmd_env(_args):
    token = read_token()
    base = CONFIG["api_base"].rstrip("/") + "/sandbox-ai"
    print(f"export ANTHROPIC_BASE_URL={base}")
    print(f"export ANTHROPIC_API_KEY={token}")
    print("# run: eval \"$(python -m sandbox env)\"")


def cmd_grade(args):
    path = Path(args.predictions)
    if not path.exists():
        sys.exit(f"File not found: {path}")
    predictions = []
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            predictions.append(json.loads(line))
        except json.JSONDecodeError:
            sys.exit(f"Line {i} is not valid JSON.")
    sha = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    r = call("POST", "/grade", {"predictions": predictions, "commit_sha": sha, "dirty_worktree": dirty})
    s = r["public_score"]
    print(f"Public score (half the answer key) · accuracy {s['accuracy']:.2%} · macro F1 {s['macro_f1']:.3f}")
    hr = s["human_recall"]
    print(f"needs_human recall: {'n/a' if hr is None else f'{hr:.2%}'}")
    print("Per queue F1: " + ", ".join(f"{q} {v['f1']:.2f}" for q, v in s["per_queue"].items()))
    c = r["counts"]
    print(f"valid {c['valid']} · missing {c['missing']} · unknown ids {c['unknown_ids']} · duplicates {c['duplicates']}")
    for e in r.get("errors", []):
        print(f"  ! {e}")
    if dirty:
        print("Note: you have uncommitted changes — commit so reviewers can see what produced this score.")
    print(f"Grade runs left: {r['grade_runs_left']}")


def cmd_submit(args):
    r = call("POST", "/submit", {"repo_url": args.repo, "video_url": args.video, "note_url": args.note})
    print(r["message"])


def main():
    p = argparse.ArgumentParser(prog="python -m sandbox")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("login"); s.add_argument("token"); s.set_defaults(fn=cmd_login)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("start").set_defaults(fn=cmd_start)
    sub.add_parser("env").set_defaults(fn=cmd_env)
    g = sub.add_parser("grade"); g.add_argument("predictions"); g.set_defaults(fn=cmd_grade)
    m = sub.add_parser("submit")
    m.add_argument("--repo", required=True)
    m.add_argument("--video", required=True)
    m.add_argument("--note", required=True)
    m.set_defaults(fn=cmd_submit)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
