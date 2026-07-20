#!/usr/bin/env python3
"""Update or delete existing Clockify time entries.

Reads JSON of the form:
  {
    "updates": [
      {"id": "...", "start"?: ISO, "end"?: ISO, "project_id"?: "...", "description"?: "...", "billable"?: bool},
      ...
    ],
    "deletes": ["entry_id", ...]
  }

For updates, fields are optional — missing fields keep the entry's current value.
Outputs {"updated": [...], "deleted": [...]}.
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


def fmt_summary(start, end, project_name, description, tz):
    s = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone(tz)
    e = datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(tz)
    proj = project_name or "(no project)"
    return f"{s.strftime('%H:%M')}–{e.strftime('%H:%M')} {proj} — {description}".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON file with updates/deletes")
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

    updates = payload.get("updates") or []
    deletes = payload.get("deletes") or []
    if not updates and not deletes:
        fail("No updates or deletes in input file.", code="empty_input")

    tz = ZoneInfo(os.environ.get("TIMEZONE", "Europe/Prague"))
    headers = {"X-Api-Key": api_key}

    user_resp = requests.get(f"{CLOCKIFY_BASE}/user", headers=headers, timeout=20)
    if not user_resp.ok:
        fail(f"User fetch failed: {user_resp.status_code} {user_resp.text}", code="clockify_error")
    user = user_resp.json()
    workspace_id = os.environ.get("CLOCKIFY_WORKSPACE_ID") or user.get("defaultWorkspace")
    if not workspace_id:
        fail("No Clockify workspace found.", code="no_workspace")

    proj_resp = requests.get(
        f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/projects",
        headers=headers,
        params={"page-size": 200, "archived": "false"},
        timeout=20,
    )
    project_by_id = {p["id"]: p["name"] for p in proj_resp.json()} if proj_resp.ok else {}

    updated_results = []
    for upd in updates:
        eid = upd.get("id")
        if not eid:
            updated_results.append({"ok": False, "error": "missing id", "summary": str(upd)})
            continue

        cur_resp = requests.get(
            f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/time-entries/{eid}",
            headers=headers, timeout=20,
        )
        if not cur_resp.ok:
            updated_results.append({
                "ok": False, "id": eid,
                "error": f"fetch failed: {cur_resp.status_code} {cur_resp.text}",
                "summary": str(upd),
            })
            continue
        cur = cur_resp.json()
        ti = cur.get("timeInterval") or {}
        cur_start, cur_end = ti.get("start"), ti.get("end")

        new_start = to_utc_z(upd["start"]) if "start" in upd else cur_start
        new_end = to_utc_z(upd["end"]) if "end" in upd else cur_end
        new_desc = upd.get("description", cur.get("description", ""))
        new_pid = upd.get("project_id", cur.get("projectId"))
        new_billable = upd.get("billable", cur.get("billable", False))

        body = {
            "start": new_start,
            "end": new_end,
            "description": new_desc,
            "billable": new_billable,
        }
        if new_pid:
            body["projectId"] = new_pid
        if cur.get("tagIds"):
            body["tagIds"] = cur["tagIds"]
        if cur.get("taskId"):
            body["taskId"] = cur["taskId"]

        proj_name = project_by_id.get(new_pid, "")
        summary = fmt_summary(new_start, new_end, proj_name, new_desc, tz)

        r = requests.put(
            f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/time-entries/{eid}",
            headers=headers, json=body, timeout=20,
        )
        if r.ok:
            updated_results.append({"ok": True, "id": eid, "summary": summary})
        else:
            updated_results.append({
                "ok": False, "id": eid,
                "error": f"{r.status_code} {r.text}", "summary": summary,
            })

    deleted_results = []
    for did in deletes:
        eid = did if isinstance(did, str) else did.get("id")
        if not eid:
            deleted_results.append({"ok": False, "error": "missing id"})
            continue
        r = requests.delete(
            f"{CLOCKIFY_BASE}/workspaces/{workspace_id}/time-entries/{eid}",
            headers=headers, timeout=20,
        )
        if r.ok:
            deleted_results.append({"ok": True, "id": eid})
        else:
            deleted_results.append({
                "ok": False, "id": eid,
                "error": f"{r.status_code} {r.text}",
            })

    print(json.dumps(
        {"updated": updated_results, "deleted": deleted_results},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
