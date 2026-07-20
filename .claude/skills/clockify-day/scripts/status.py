#!/usr/bin/env python3
"""Gather context for logging Clockify entries.

Outputs JSON to stdout with: user, today, workday, logged, calendar, projects, history.
By default the data covers today; pass --date YYYY-MM-DD to gather for any other day
(useful for fixing past entries). History is always the 30 days ending now.

On error, writes JSON to stderr and exits 1.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CLOCKIFY_BASE = "https://api.clockify.me/api/v1"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

try:
    from dotenv import load_dotenv
    load_dotenv(SKILL_DIR / ".env")
except ImportError:
    pass


def fail(message, code="error"):
    print(json.dumps({"error": message, "code": code}), file=sys.stderr)
    sys.exit(1)


def clockify_get(path, params=None):
    api_key = os.environ["CLOCKIFY_API_KEY"]
    r = requests.get(
        f"{CLOCKIFY_BASE}{path}",
        headers={"X-Api-Key": api_key},
        params=params,
        timeout=20,
    )
    if not r.ok:
        raise RuntimeError(f"Clockify GET {path} failed: {r.status_code} {r.text}")
    return r.json()


def clockify_get_paginated(path, params=None, page_size=200):
    items = []
    page = 1
    base_params = dict(params or {})
    while True:
        p = dict(base_params, page=page, **{"page-size": page_size})
        chunk = clockify_get(path, p)
        items.extend(chunk)
        if len(chunk) < page_size:
            break
        page += 1
    return items


def get_calendar_events(time_min, time_max):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        fail(
            "Google API libraries not installed. Run: "
            f"pip install -r {SKILL_DIR / 'requirements.txt'}",
            code="missing_deps",
        )

    secret_path = SKILL_DIR / "client_secret.json"
    token_path = SKILL_DIR / "token.json"

    if not secret_path.exists():
        fail(
            f"client_secret.json not found at {secret_path}. "
            "See README.md for Google Cloud OAuth setup.",
            code="missing_client_secret",
        )

    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                fail(
                    f"Token refresh failed ({e}). Delete {token_path} and rerun.",
                    code="invalid_grant",
                )
        else:
            print(
                "A browser window should open — authorize with Google and come back. "
                "(One-time setup.)",
                file=sys.stderr,
            )
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    resp = service.events().list(
        calendarId="primary",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for ev in resp.get("items", []):
        start = ev.get("start", {})
        end = ev.get("end", {})
        if "dateTime" not in start or "dateTime" not in end:
            continue
        title = (ev.get("summary") or "").strip()
        if not title:
            continue
        if "[personal]" in title.lower():
            continue
        attendees = ev.get("attendees") or []
        if any(a.get("self") and a.get("responseStatus") == "declined" for a in attendees):
            continue
        try:
            s = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            e = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if (e - s).total_seconds() < 15 * 60:
            continue
        events.append({
            "id": ev.get("id"),
            "title": title,
            "start": s.isoformat(),
            "end": e.isoformat(),
            "location": ev.get("location", ""),
        })
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="ISO date YYYY-MM-DD; default is today in local TZ")
    parser.add_argument(
        "--projects",
        nargs="?",
        const="",
        default=None,
        metavar="FILTER",
        help="Output only active projects (skips calendar/logged/history). "
             "Optional FILTER does case-insensitive substring match on project name.",
    )
    args = parser.parse_args()

    if not os.environ.get("CLOCKIFY_API_KEY"):
        fail(
            "CLOCKIFY_API_KEY not set. Copy .env.example to .env in the skill dir "
            f"({SKILL_DIR}) and fill in the key from Clockify Profile → Preferences → API.",
            code="missing_api_key",
        )

    tz_name = os.environ.get("TIMEZONE", "Europe/Prague")
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        fail(f"Invalid TIMEZONE: {tz_name}", code="bad_timezone")

    workday_start = os.environ.get("WORKDAY_START", "09:00")
    workday_end = os.environ.get("WORKDAY_END", "17:00")

    try:
        user = clockify_get("/user")
    except Exception as e:
        fail(f"Clockify user fetch failed: {e}", code="clockify_error")

    workspace_id = os.environ.get("CLOCKIFY_WORKSPACE_ID") or user.get("defaultWorkspace")
    if not workspace_id:
        fail(
            "No Clockify workspace found. Set CLOCKIFY_WORKSPACE_ID env var.",
            code="no_workspace",
        )
    user_id = user["id"]

    if args.projects is not None:
        try:
            projects = clockify_get_paginated(
                f"/workspaces/{workspace_id}/projects",
                params={"archived": "false"},
            )
        except Exception as e:
            fail(str(e), code="clockify_error")
        if args.projects:
            needle = args.projects.lower()
            projects = [p for p in projects if needle in p["name"].lower()]
        print(json.dumps(
            [{"id": p["id"], "name": p["name"]} for p in projects],
            indent=2, ensure_ascii=False,
        ))
        return

    if args.date:
        try:
            target_local = datetime.fromisoformat(args.date).date()
        except ValueError:
            fail(f"Invalid --date {args.date}; expected YYYY-MM-DD", code="bad_date")
    else:
        target_local = datetime.now(tz).date()
    day_start = datetime.combine(target_local, datetime.min.time(), tzinfo=tz).astimezone(timezone.utc)
    day_end = day_start + timedelta(days=1)

    try:
        entries_today = clockify_get_paginated(
            f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
            params={
                "start": day_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": day_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        projects = clockify_get_paginated(
            f"/workspaces/{workspace_id}/projects",
            params={"archived": "false"},
        )
        history_start = day_start - timedelta(days=30)
        history_entries = clockify_get_paginated(
            f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
            params={
                "start": history_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": day_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
    except Exception as e:
        fail(str(e), code="clockify_error")

    project_by_id = {p["id"]: p["name"] for p in projects}

    logged = []
    for e in entries_today:
        ti = e.get("timeInterval") or {}
        s, en = ti.get("start"), ti.get("end")
        if not s or not en:
            continue
        logged.append({
            "id": e["id"],
            "start": datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(tz).isoformat(),
            "end": datetime.fromisoformat(en.replace("Z", "+00:00")).astimezone(tz).isoformat(),
            "project_id": e.get("projectId"),
            "project_name": project_by_id.get(e.get("projectId"), ""),
            "description": e.get("description", ""),
        })
    logged.sort(key=lambda x: x["start"])

    history = {}
    seen = {}
    sorted_history = sorted(
        history_entries,
        key=lambda x: (x.get("timeInterval") or {}).get("start") or "",
        reverse=True,
    )
    for e in sorted_history:
        pid = e.get("projectId")
        desc = (e.get("description") or "").strip()
        if not pid or not desc:
            continue
        bucket = history.setdefault(pid, [])
        seen_set = seen.setdefault(pid, set())
        if desc in seen_set or len(bucket) >= 10:
            continue
        bucket.append(desc)
        seen_set.add(desc)

    try:
        calendar = get_calendar_events(day_start, day_end)
    except SystemExit:
        raise
    except Exception as e:
        fail(f"Calendar fetch failed: {e}", code="calendar_error")

    output = {
        "user": {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "timezone": tz_name,
        },
        "date": target_local.isoformat(),
        "workday": {"start": workday_start, "end": workday_end},
        "logged": logged,
        "calendar": calendar,
        "projects": [{"id": p["id"], "name": p["name"]} for p in projects],
        "history": history,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
