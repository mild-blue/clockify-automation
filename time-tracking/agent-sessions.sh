#!/usr/bin/env bash
# agent-sessions.sh — which Claude Code agent sessions ran on the dev server, when.
#
# Reads the Claude Code transcripts on the remote dev box (~/.claude/projects/*/*.jsonl)
# over NetBird SSH and prints METADATA ONLY as JSON: per session its worktree (cwd),
# git branch and the timestamps of "user"-type events. Message content is never read
# out. Note: "user" events include tool results, so an agent that runs on its own
# still produces timestamps — gate on ActivityWatch AFK data to know when YOU were
# actually at the keyboard, and use this only to attribute those blocks to a
# worktree / issue (worktrees are named after the issue, e.g. 17255-chat-image-poc).
#
# Usage:  time-tracking/agent-sessions.sh 2026-09-14 2026-09-19 > agents.json
# Env:    AGENT_HOST (default ai-dev-server-jan-kubant), AGENT_USER (default ubuntu)
# First call per NetBird login opens a browser SSO page.
set -euo pipefail
FROM="${1:?from date YYYY-MM-DD}"; TO="${2:?to date YYYY-MM-DD (exclusive)}"
HOST="${AGENT_HOST:-ai-dev-server-jan-kubant}"; USER_="${AGENT_USER:-ubuntu}"
NB=/Applications/NetBird.app/Contents/MacOS/netbird

"$NB" ssh -u "$USER_" "$HOST" "python3 - '$FROM' '$TO'" <<'PY' 2>/dev/null | grep '^JSON:' | sed 's/^JSON://'
import json, os, glob, sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
TZ = ZoneInfo("Europe/Prague")
lo = datetime.fromisoformat(sys.argv[1]).replace(tzinfo=TZ)
hi = datetime.fromisoformat(sys.argv[2]).replace(tzinfo=TZ)
out = []
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    if os.path.getmtime(f) < lo.timestamp():
        continue
    cwd = br = None; times = []
    for line in open(f, errors="ignore"):
        try: m = json.loads(line)
        except Exception: continue
        if m.get("type") != "user" or m.get("isSidechain") or not m.get("timestamp"):
            continue
        t = datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).astimezone(TZ)
        if lo <= t < hi:
            times.append(t.strftime("%Y-%m-%d %H:%M"))
            cwd = m.get("cwd") or cwd; br = m.get("gitBranch") or br
    if times:
        out.append({"session": os.path.basename(f)[:8], "cwd": cwd, "branch": br, "times": sorted(times)})
print("JSON:" + json.dumps(out))
PY
