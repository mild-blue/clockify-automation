---
name: clockify-day
description: Help the user log today's time entries in Clockify based on their Google Calendar. Use this skill whenever the user asks to log their time, fill in their day, check what they've logged, see calendar gaps, or asks anything resembling "what should I log", "did I forget anything", "fill in my Clockify", "doplň mi den", "co jsem dnes dělal", "log my meetings", or mentions Clockify and a current/recent day in the same message. Trigger this skill even if the user just says "I should log my time" or "what did I do today" — those phrasings are the right context for this workflow.
---

# Clockify Day

A four-step workflow: **gather → reason → confirm → write**. The scripts handle gather and write. The reasoning and confirmation are yours — that's the part that needs judgment.

## Step 1 — Gather

Run the status script:

```bash
python <skill_dir>/scripts/status.py
# For a different day (e.g. fixing yesterday):
python <skill_dir>/scripts/status.py --date 2026-05-05
# Just project lookup (skips calendar — fast and won't trigger OAuth):
python <skill_dir>/scripts/status.py --projects           # all active projects
python <skill_dir>/scripts/status.py --projects slp       # filter by name substring
```

Use the absolute path to this skill's `scripts/status.py`. It outputs JSON to stdout with these top-level keys:

- `user` — name, email, timezone
- `date` — ISO date the data covers (today by default, or `--date` if provided)
- `workday` — start/end times (used to spot gaps)
- `logged` — that date's existing Clockify entries, sorted by start. Each has `id`, `start`, `end`, `project_id`, `project_name`, `description` — keep the `id`s if you might edit or delete.
- `calendar` — that date's calendar events (declined / all-day / `[personal]` / <15 min already filtered out)
- `projects` — all active Clockify projects (`id` + `name`)
- `history` — `{project_id: [recent descriptions]}` from the last 30 days, deduped, capped to 10 per project

If the script errors, it writes JSON to stderr (e.g. `{"error": "...", "code": "missing_api_key"}`). See **Failure modes** below.

## Step 2 — Reason

**First, read `<skill_dir>/notes.md`.** It contains the user's personal logging rules and project-mapping conventions. Anything in there overrides guesses you'd otherwise make from `history` alone.

Then walk the calendar events in time order. For each one, decide:

- **Skip** if any of these apply:
  - Already covered by an existing logged entry (overlap > 50%).
  - Looks personal or like a break: lunch, oběd, coffee, gym, doctor, lékař, transit, "OOO", "PTO", dentist, etc.
  - All-hands, social events, retros, all-team standups the user wouldn't normally bill — unless the user's history shows they do log these.
- **Propose** otherwise. Pick the Clockify project that best matches based on the history for that project (descriptions in `history[project_id]`). Write a concise description, 5–10 words, in the user's own style.

**Match the user's language.** Look at the descriptions in `history` — if past entries for the chosen project are in Czech, propose in Czech. If they're in English, English. If mixed, match the language of the most-similar past entries for that project. Don't translate the calendar event title verbatim; rephrase in the style the history shows.

**Ambiguous mappings get flagged, not asked.** If a calendar event could plausibly map to two projects, pick the most likely one and mark it `[low confidence]` in the rendered table. Don't pause mid-flow to ask — surfacing ambiguity in the proposal table lets the user fix it in one pass instead of being interrogated event by event.

**Never propose entries that overlap already-logged time.** Clockify won't dedupe; the user has to clean up by hand.

You can also note **gaps** in the workday (between `workday.start` and `workday.end`) where there's no calendar event and no logged entry. Mention them as info, but don't propose entries for them — there's no source. If the user wants to log into a gap, they'll tell you what they did.

## Step 3 — Confirm

Render a clear table. Use this exact shape:

```
Logged so far today (Xh Ym):
  • HH:MM–HH:MM  Project — Description
  ...

Proposals:
  1. HH:MM–HH:MM  Project — Description
       ↳ from: <calendar event title>
  2. HH:MM–HH:MM  Project — Description  [low confidence]
       ↳ from: <calendar event title>

Skipped (FYI, not proposed):
  • HH:MM–HH:MM  <event title>  — looks personal
  • HH:MM–HH:MM  <event title>  — already covered by entry above

Gaps (not proposing — tell me what you did):
  • HH:MM–HH:MM
```

Then ask something like: **"Reply `create 1,3` to log those, `create all` for everything, or tell me what to change."**

**Wait for explicit, unambiguous confirmation before Step 4.**

- "create 1,2", "create all", "yes do it", "log them" → proceed.
- "looks good", "ok", "sure", "👍" alone → ask back for the specific numbers. The reason: those phrases can mean "I read it" or "fine I guess" without actually confirming, and creating the wrong entries means real billable hours mis-allocated to the wrong client.
- Edits ("change 2 to project X", "make 1 a bit shorter") → update your in-memory list and re-render the table, then ask again.

## Step 4 — Write

Build a JSON file with the confirmed entries and call the create script.

File format:

```json
{
  "entries": [
    {
      "start": "2026-05-06T11:00:00+02:00",
      "end": "2026-05-06T12:00:00+02:00",
      "project_id": "5e4b...abc",
      "description": "Follow-up call s klientem"
    }
  ]
}
```

Save to `/tmp/clockify_create_<timestamp>.json` and run:

```bash
python <skill_dir>/scripts/create.py --input /tmp/clockify_create_<timestamp>.json
```

The script prints `{"created": [...]}`. Each result is either:
- `{"ok": true, "id": "...", "summary": "HH:MM–HH:MM Project — Desc"}`, or
- `{"ok": false, "error": "...", "summary": "..."}`

Report back: how many were created, any failures with the verbatim error, and a one-line summary per entry. **Don't silently retry on failure** — surface it. If a 403 comes back, that usually means workspace permissions; pass the error text through unchanged so the user can act on it.

## Editing or deleting existing entries

When the user asks to fix, move, shorten, retime, reproject, or delete already-logged entries (e.g. "fix the overlap on yesterday's standup", "move that to project X", "delete the duplicate"), use the same gather → reason → confirm → write rhythm but with `edit.py` instead of `create.py`.

1. **Gather** with `status.py --date <day>` if it's not today. You need each affected entry's `id` from the `logged` array.
2. **Render before/after** for every change. Group updates and deletes in one numbered list so the user can confirm in a single pass:

   ```
   Edit:
     1. BEFORE: 09:30–09:50  (no project) — Standup slp.blue
        AFTER:  09:30–09:45  slp - byznys — Standup slp.blue
     2. BEFORE: 13:00–14:00  (no project) — Iveta Honza
        AFTER:  13:00–14:00  ECL2 — Iveta Honza

   Delete:
     3. 14:00–15:00  ProjectX — duplicate of #2
   ```

   Show only fields that change in the AFTER line if you want, but keep the BEFORE complete so the user sees what's at stake. For deletes, show the full entry so they can verify they're killing the right one.

3. **Wait for explicit numbered confirmation.** "apply 1,2,3", "do all of those", "yes apply" all qualify. "looks good" alone doesn't — Clockify has no undo, and a wrong edit silently corrupts billing history. The bar is the same as for creates.

4. **Write** to `/tmp/clockify_edit_<timestamp>.json`:

   ```json
   {
     "updates": [
       {"id": "abc123", "end": "2026-05-05T09:45:00+02:00", "project_id": "601fa..."},
       {"id": "def456", "project_id": "6203df..."}
     ],
     "deletes": ["ghi789"]
   }
   ```

   Update fields are optional — anything you omit keeps its current value. Then run:

   ```bash
   python <skill_dir>/scripts/edit.py --input /tmp/clockify_edit_<timestamp>.json
   ```

   Output:

   ```json
   {
     "updated": [{"ok": true, "id": "abc123", "summary": "..."}, ...],
     "deleted": [{"ok": true, "id": "ghi789"}, ...]
   }
   ```

5. **Report verbatim failures.** Don't retry silently. A 403 usually means workspace permissions; a 404 means the entry was already gone.

## Environment

Both scripts auto-load `<skill_dir>/.env` if it exists (see `.env.example` for the template). Real shell env vars override `.env` values.

Required:

- `CLOCKIFY_API_KEY` — from Clockify Profile → Preferences → API.

Optional:

- `CLOCKIFY_WORKSPACE_ID` — defaults to the user's `defaultWorkspace`. Set this if they have multiple workspaces and the default isn't the right one.
- `WORKDAY_START` (default `09:00`) — used to spot gaps to mention.
- `WORKDAY_END` (default `17:00`).
- `TIMEZONE` (default `Europe/Prague`) — IANA name. Drives "what counts as today".

OAuth files live in this skill's directory (next to `SKILL.md`):

- `client_secret.json` — user-provided OAuth client (Desktop app type from Google Cloud Console). One-time setup; see `README.md`.
- `token.json` — auto-created and refreshed after the first run. Don't commit it.

## What never to do

- **Never call create.py without explicit per-number confirmation.** "looks good" isn't enough — see Step 3.
- **Never propose entries that overlap existing logged time.** No auto-dedupe in Clockify; the user has to clean up manually.
- **Never include attendee email lists or sensitive event content verbatim** in proposal descriptions. Time entries are usually visible to managers and clients in reports, so keep descriptions about the work, not who was there.
- **Never edit or delete existing entries without showing the user the exact before/after and getting explicit numbered confirmation.** Clockify has no undo — silently corrupting billing history is the worst failure mode this skill has. Bulk shortcuts like "fix everything" still need a rendered list and a per-entry "yes". If the user is unsure about a specific entry, route them to the Clockify UI.
- **Never output the raw contents of `client_secret.json` or `token.json`.** Both are credentials.

## Failure modes

| Code from stderr | What it means | What to tell the user |
|---|---|---|
| `missing_api_key` | `CLOCKIFY_API_KEY` not set | Tell them to copy `.env.example` to `.env` in the skill dir and fill in the key from Clockify Profile → Preferences → API. Don't proceed. |
| `missing_client_secret` | `client_secret.json` not in the skill dir | Point them to `README.md` Google Cloud setup. |
| `invalid_grant` | `token.json` is stale or the OAuth app changed | Tell them to delete `token.json` from the skill dir and rerun. |
| `missing_deps` | Google libraries not installed | `pip install -r <skill_dir>/requirements.txt` |
| `no_workspace` | Couldn't determine workspace | Ask them to set `CLOCKIFY_WORKSPACE_ID`. |
| `clockify_error` | Clockify API call failed | Surface the error verbatim. A 403 usually means workspace permissions. |
| `calendar_error` | Calendar API call failed | Surface verbatim; if it mentions auth, suggest deleting `token.json`. |

First-run OAuth: the script will pop a browser window. Tell the user "a browser window should open — authorize and come back. This only happens once."

No calendar events for today is a normal case — say so and offer to log time manually if they tell you what they did.
