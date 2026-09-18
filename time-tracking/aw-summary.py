#!/usr/bin/env python3
"""aw-summary.py — reconstruct what actually happened, day by day, from ActivityWatch.

Prints, for each day in [FROM, TO):
  * active blocks  — aw-watcher-afk "not-afk" spans, merged across gaps < MERGE_MIN,
                     dropping blocks shorter than MIN_BLOCK. Idle gaps are breaks:
                     never log through them (see notes.md).
  * calls          — aw-watcher-meet events (Meet/Zoom/Teams in any tab). Calls
                     override idle: a call is meeting time even with no keyboard.
  * apps           — time per app (frontmost window).
  * titles/hour    — dominant VS Code / terminal / Claude window titles per hour. The
                     VS Code title leads with the git branch (window.title setting).
  * agents         — with --agents <agents.json> (output of agent-sessions.sh): for
                     every active block, which Claude agent worktrees had activity in
                     it, as a share. Worktree names carry the issue number.

Usage:
  time-tracking/aw-summary.py 2026-09-14 2026-09-19
  time-tracking/aw-summary.py 2026-09-14 2026-09-19 --agents ~/TimeTracking/agents.json

Stdlib only; talks to the local ActivityWatch server (localhost:5600).
"""
import argparse
import json
import socket
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Prague")
MERGE_MIN = 10   # merge active spans separated by less than this many minutes
MIN_BLOCK = 7    # ignore active blocks shorter than this many minutes
HOST = socket.gethostname()
AW = "http://localhost:5600/api/0/buckets"
TITLE_APPS = {"Code", "Claude", "Terminal", "Terminál", "iTerm2", "Ghostty", "Zed", "Microsoft Word"}


def events(bucket):
    try:
        with urllib.request.urlopen(f"{AW}/{bucket}/events?limit=-1", timeout=60) as r:
            return json.load(r)
    except Exception:
        return []


def ts(e):
    return datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).astimezone(TZ)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start"), ap.add_argument("end", help="exclusive")
    ap.add_argument("--agents", help="JSON from time-tracking/agent-sessions.sh")
    a = ap.parse_args()
    lo = datetime.fromisoformat(a.start).replace(tzinfo=TZ)
    hi = datetime.fromisoformat(a.end).replace(tzinfo=TZ)

    afk = events(f"aw-watcher-afk_{HOST}")
    win = events(f"aw-watcher-window_{HOST}")
    meet = events(f"aw-watcher-meet_{HOST}")

    agent_ev = []  # (datetime, worktree)
    if a.agents:
        for s in json.load(open(a.agents)):
            wt = (s.get("cwd") or "").replace("/home/ubuntu/", "").replace("slp/.claude/worktrees/", "wt:")
            for t in s["times"]:
                agent_ev.append((datetime.strptime(t, "%Y-%m-%d %H:%M").replace(tzinfo=TZ), wt))

    day = lo
    while day < hi:
        nxt = day + timedelta(days=1)
        inday = lambda e: day <= ts(e) < nxt
        spans = sorted((ts(e), ts(e) + timedelta(seconds=e["duration"]))
                       for e in afk if inday(e) and e["data"].get("status") == "not-afk")
        blocks = []
        for s, en in spans:
            if blocks and (s - blocks[-1][1]).total_seconds() < MERGE_MIN * 60:
                blocks[-1][1] = max(blocks[-1][1], en)
            else:
                blocks.append([s, en])
        blocks = [b for b in blocks if (b[1] - b[0]).total_seconds() >= MIN_BLOCK * 60]
        total = sum((b[1] - b[0]).total_seconds() for b in blocks) / 3600
        print(f"\n######## {day:%a %Y-%m-%d}   active ~{total:.1f} h")
        for s, en in blocks:
            line = f"  active {s:%H:%M}-{en:%H:%M}"
            if agent_ev:
                c = Counter(wt for t, wt in agent_ev if s <= t < en)
                n = sum(c.values())
                line += "   agents: " + (", ".join(f"{k} {v * 100 // n}%" for k, v in c.most_common(3)) if n else "-")
            print(line)
        calls = sorted((ts(e), e) for e in meet if inday(e) and e["duration"] > 120)
        for t, e in calls:
            print(f"  call   {t:%H:%M}-{t + timedelta(seconds=e['duration']):%H:%M} {e['data'].get('service')}")
        apps = Counter()
        hours = defaultdict(Counter)
        for e in win:
            if not inday(e):
                continue
            app = e["data"].get("app", "?")
            apps[app] += e["duration"]
            if app in TITLE_APPS:
                title = e["data"].get("title", "").replace(" [SSH: ai-dev-server-jan-kubant]", "")[:70]
                hours[ts(e).hour][f"{app}: {title}"] += e["duration"]
        print("  apps: " + ", ".join(f"{k} {v / 60:.0f}m" for k, v in apps.most_common(6) if v > 300))
        for h in sorted(hours):
            top = [(k, v) for k, v in hours[h].most_common(2) if v > 240]
            if top:
                print(f"   {h:02d}h " + " | ".join(f"{k} ({v / 60:.0f}m)" for k, v in top))
        day = nxt


if __name__ == "__main__":
    main()
