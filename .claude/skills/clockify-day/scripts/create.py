#!/usr/bin/env python3
"""Create Clockify time entries from a JSON spec.

Reads {"entries": [{"start", "end", "project_id", "description", "billable"?}, ...]}
Outputs {"created": [{"ok", "id"?, "error"?, "summary"}, ...]}.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

SKILL_DIR = Path(__file__).resolve().parent.parent
CLOCKIFY_BASE = "https://api.clockify.me/api/v1"

try:
    from dotenv import load_dotenv
    load_dotenv(SKILL_DIR / ".env")
except ImportError:
    pass


def fail(message, code="error"):
    print(json.dumps({"error": message, "code": code}), file=sys.stderr)
    sys.exit(1)


def to_utc_z(s):
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_summary(entry, project_name, tz):
    s = datetime.fromisoformat(entry["start"].replace("Z", "+00:00")).astimezone(tz)
    e = datetime.fromisoformat(entry["end"].replace("Z", "+00:00")).astimezone(tz)
    desc = entry.get("description", "")
    proj = project_name or "(no project)"
    return f"{s.strftime('%H:%M')}–{e.strftime('%H:%M')} {proj} — {desc}".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON file with entries")
    args = parser.parse_args()

    api_key = os.environ.get("CLOCKIFY_API_KEY")
    if not api_key:
        fail("CLOCKIFY_API_KEY not set.", code="missing_api_key")

    try:
        with open(args.input) as f:
            payload = json.load(f)
    except FileNotFoundError:
        fail(f"Input file not found: {args.input}", code="missing_input")
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {args.input}: {e}", code="bad_input")

    entries = payload.get("entries") or []
    if not entries:
        fail("No entries in input file.", code="empty_input")

    tz = ZoneInfo(os.environ.get("TIMEZONE", "Europe/Prague"))
    headers = {"X-Api-Key": api_key}

    user_resp = requests.get(f"{CLOCKIFY_BASE}/user", headers=headers, timeout=20)
    if not user_resp.ok:
        fail(f"User fetch failed: {user_resp.status_code} {user_resp.text}", code="clockify_error")
    user = user_resp.json()
    workspace_id = os.environ.get("CLOCKIFY_WORKSPACE_ID") or user.get("defaultWorkspace")
    if not workspace_id:
        fail("No Clockify workspace found. Set CLOCKIFY_WORKSPACE_ID.", code="no_workspace")

    proj_resp = requests.get(
        f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/projects",
        headers=headers,
        params={"page-size": 200, "archived": "false"},
        timeout=20,
    )
    project_by_id = {p["id"]: p["name"] for p in proj_resp.json()} if proj_resp.ok else {}

    results = []
    for entry in entries:
        try:
            body = {
                "start": to_utc_z(entry["start"]),
                "end": to_utc_z(entry["end"]),
                "description": entry.get("description", ""),
                "billable": entry.get("billable", False),
            }
            if entry.get("project_id"):
                body["projectId"] = entry["project_id"]
        except (KeyError, ValueError) as e:
            results.append({"ok": False, "error": f"Bad entry: {e}", "summary": str(entry)})
            continue

        project_name = project_by_id.get(entry.get("project_id"), "")
        summary = fmt_summary(entry, project_name, tz)

        r = requests.post(
            f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/time-entries",
            headers=headers,
            json=body,
            timeout=20,
        )
        if r.ok:
            results.append({"ok": True, "id": r.json().get("id"), "summary": summary})
        else:
            results.append({"ok": False, "error": f"{r.status_code} {r.text}", "summary": summary})

    print(json.dumps({"created": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
