#!/usr/bin/env python3
"""aw-watcher-meet — detect active video calls regardless of foreground.

ActivityWatch's window watcher only records the *frontmost* app, and the web
watcher only the *active* tab of the focused window. So a Google Meet / Zoom /
Teams call running in a background tab (while you're in VS Code, notes, etc.)
is invisible, and because you're not typing during a call the AFK watcher logs
it as idle. Both together mean calls silently vanish from the reconstructed day.

This watcher polls every POLL seconds for a live call in ANY Chrome/Brave tab
(matching real meeting-URL patterns, not just an idle landing page) and posts a
heartbeat to its own bucket. Consecutive heartbeats merge into one continuous
"call" event (pulsetime > POLL), so the reconstruction can treat those spans as
meeting time, overriding AFK-idle.

Stdlib only. Reads Chrome/Brave tabs via AppleScript WITHOUT launching them
(guarded by System Events process check). First run triggers a one-time macOS
Automation permission prompt.

Env:
  AW_HOST    default localhost:5600
  POLL       seconds between polls (default 30)
"""
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

AW_HOST = os.environ.get("AW_HOST", "localhost:5600")
POLL = int(os.environ.get("POLL", "30"))
PULSETIME = POLL * 3 + 15  # bridge a couple of missed polls into one event
HOST = socket.gethostname()
BUCKET = f"aw-watcher-meet_{HOST}"
BASE = f"http://{AW_HOST}/api/0"

# Real call URLs, not idle landing/home tabs.
CALL_PATTERNS = [
    ("google-meet", re.compile(r"meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}", re.I)),
    ("zoom", re.compile(r"zoom\.us/(j|wc|s)/\d", re.I)),
    ("teams", re.compile(r"teams\.(microsoft|live)\.com/.*(meetup-join|/l/meeting|/_#/l/)", re.I)),
    ("whereby", re.compile(r"whereby\.com/[\w-]+", re.I)),
]

TABS_APPLESCRIPT = r'''
tell application "System Events"
    set chromeUp to (exists process "Google Chrome")
    set braveUp to (exists process "Brave Browser")
end tell
set out to ""
if chromeUp then
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                set out to out & (URL of t) & linefeed
            end repeat
        end repeat
    end tell
end if
if braveUp then
    tell application "Brave Browser"
        repeat with w in windows
            repeat with t in tabs of w
                set out to out & (URL of t) & linefeed
            end repeat
        end repeat
    end tell
end if
return out
'''


def _req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read()


def ensure_bucket():
    try:
        _req("POST", f"/buckets/{BUCKET}", {
            "client": "aw-watcher-meet",
            "type": "call.active",
            "hostname": HOST,
        })
    except Exception:
        pass  # already exists -> AW returns non-2xx; that's fine


def open_tabs():
    try:
        p = subprocess.run(["osascript", "-"], input=TABS_APPLESCRIPT,
                           capture_output=True, text=True, timeout=15)
        return p.stdout
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] osascript error: {e}", flush=True)
        return ""


def detect_call(tabs):
    for service, pat in CALL_PATTERNS:
        if pat.search(tabs):
            return service
    return None


def heartbeat(service):
    now = datetime.now(timezone.utc).isoformat()
    _req("POST", f"/buckets/{BUCKET}/heartbeat?pulsetime={PULSETIME}", {
        "timestamp": now,
        "duration": 0,
        "data": {"status": "call", "service": service},
    })


def main():
    ensure_bucket()
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] aw-watcher-meet started "
          f"(bucket={BUCKET}, poll={POLL}s)", flush=True)
    last = None
    while True:
        try:
            service = detect_call(open_tabs())
            if service:
                heartbeat(service)
                if service != last:
                    print(f"[{datetime.now():%H:%M:%S}] call active: {service}", flush=True)
            elif last:
                print(f"[{datetime.now():%H:%M:%S}] call ended", flush=True)
            last = service
        except Exception as e:
            print(f"[{datetime.now():%H:%M:%S}] loop error: {e}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    sys.exit(main())
