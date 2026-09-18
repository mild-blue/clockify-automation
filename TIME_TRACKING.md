# Local time tracking with ActivityWatch

This machine runs [ActivityWatch](https://activitywatch.net/) as a **local, no-cloud, no-account**
automatic activity tracker. Its purpose is to reconstruct *what was actually worked on* during the
day (apps, window titles, code files, URLs, idle time) so those activities can be turned into
Clockify time entries — complementing the calendar-based [`clockify-day`](.claude/skills/clockify-day)
skill, which only knows about scheduled meetings.

> **Why not screenshots / ManicTime?**
> The original idea was a screenshotter (ManicTime or `screencapture`). It was rejected because
> (a) work screens may contain GDPR-sensitive lab/hospital (Art. 9 health) material, so storing
> pixels — and especially sending them to an AI assistant to summarise — is an unnecessary data
> transfer; and (b) ManicTime's screenshot feature requires a paid server/account. ActivityWatch
> records lightweight *metadata* (app + title + URL + file), which is enough to reconstruct a day
> while keeping the sensitive-data footprint low. The captured signals (URLs, code paths, app
> timeline) were confirmed not to contain patient data.

## Architecture

Everything runs locally; the server listens on `http://localhost:5600` and stores data in
`~/Library/Application Support/activitywatch/`. Nothing leaves the machine except summaries that are
explicitly requested.

| Watcher | What it records | Install |
| --- | --- | --- |
| `aw-watcher-window` | frontmost app + window title | bundled with ActivityWatch |
| `aw-watcher-afk` | active / idle (away-from-keyboard) | bundled |
| `aw-watcher-vscode` | file path, project/workspace, language, duration | VS Code extension `activitywatch.aw-watcher-vscode` |
| `aw-watcher-web` | URL + page title per tab | Chrome/Brave extension ([Web Watcher](https://chromewebstore.google.com/detail/activitywatch-web-watcher/nglaklhklhcoonedhgnpgddginnjdadi)) |
| `aw-watcher-meet` | active video call (Meet/Zoom/Teams/Whereby) in **any** tab, even backgrounded | custom, this repo — see below |

Local git history (commits, branch, changed files) is read directly as an extra signal at
reconstruction time.

## Install (macOS, done 2026-07-21)

```bash
brew install --cask activitywatch                          # v0.13.2 (Intel build, runs via Rosetta 2)
code --install-extension activitywatch.aw-watcher-vscode   # VS Code watcher
# Web watcher: add the "ActivityWatch Web Watcher" extension in Chrome and Brave (same Chrome Web Store link)
```

ActivityWatch is set to launch at login via a macOS **Login Item** (hidden).

## Detecting calls (`aw-watcher-meet`)

The bundled watchers miss video calls: the window watcher only records the
*frontmost* app and the web watcher only the *active tab of the focused window*,
so a Google Meet / Zoom / Teams call in a **background tab** (while you're in VS
Code, notes, etc.) is invisible — and since you don't type during a call, the
AFK watcher logs it as **idle**. Calls therefore silently drop out of the day.

`time-tracking/aw-watcher-meet.py` (in this repo) fixes that. Every `POLL`
seconds (default 30) it reads **all** Chrome/Brave tabs via AppleScript — without
launching them — matches real meeting-URL patterns (a Meet code, `zoom.us/j|wc|s/…`,
Teams `meetup-join`, Whereby), and posts a heartbeat to its own bucket
`aw-watcher-meet_<host>` (type `call.active`). Consecutive heartbeats merge into
one continuous "call" event (pulsetime > poll).

Install (already done on this machine):

```bash
cp time-tracking/aw-watcher-meet.py ~/TimeTracking/aw-watcher-meet.py
cp time-tracking/blue.mild.aw-watcher-meet.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/blue.mild.aw-watcher-meet.plist
# first run triggers a one-time macOS Automation prompt ("... wants to control
# Google Chrome") — approve it, or detection stays empty (the watcher retries safely).
```

Confirm / restart / stop:

```bash
tail -f ~/TimeTracking/aw-watcher-meet.log
curl -s "http://localhost:5600/api/0/buckets/aw-watcher-meet_$(hostname)/events?limit=5" | python3 -m json.tool
launchctl kickstart -k gui/$(id -u)/blue.mild.aw-watcher-meet   # restart
launchctl bootout gui/$(id -u)/blue.mild.aw-watcher-meet        # stop
```

**Reconstruction rule:** a span covered by an `aw-watcher-meet` event is a
**meeting** — count it as work (billable per the calendar/project) even when the
AFK watcher shows idle and even when Meet was never in the foreground. Only
browser calls are caught; native Zoom/Teams desktop apps still rely on the
window watcher (foreground) — a mic-in-use signal could extend this later.

## Start / stop / confirm

```bash
curl -s http://localhost:5600/api/0/info    # confirm running (returns JSON when up)
open -a ActivityWatch                        # start
open http://localhost:5600                   # local dashboard (timeline UI)

# stop completely (pauses all tracking):
killall -q aw-qt aw-server aw-watcher-afk aw-watcher-window aw-watcher-window-macos
```

There is also an ActivityWatch **menu-bar icon** for quitting.

## VS Code window title carries the git branch

Most work happens in VS Code over Remote-SSH, often with Claude Code in the
integrated terminal. The `aw-watcher-vscode` extension is blind there (it logs
`unknown` for remote files), so the **window title** is the signal. It is set in the
*local* VS Code user settings (`~/Library/Application Support/Code/User/settings.json`,
not in this repo) to lead with the branch:

```json
"window.title": "${activeRepositoryBranchName}${separator}${activeEditorShort}${separator}${rootName}${separator}${remoteName}"
```

Reload VS Code after changing it. Titles then look like
`docs/16568-chatbot-legal-adr-0013 — email-ai-asistent.md — ubuntu — SSH: ai-dev-server-jan-kubant`.

## Claude agents on the dev server (NetBird)

The real task signal is which **Claude Code agent** was being driven. Agents run
on the dev box **`ai-dev-server-jan-kubant`** (user `ubuntu`), reached over
**NetBird SSH**, one **git worktree per agent** under `~/slp/.claude/worktrees/`,
named after the issue (`17255-chat-image-poc`, `review-fix-17263`, `legal-adr` → #16568).
Several agents can share a branch, so branch / window title alone can't separate them.

**Access.** NetBird asks for a browser SSO login (netbird.mild.blue) and, in practice,
does not keep the token between calls — expect a login page per connection. Use
NetBird's own client (plain `ssh` through the NetBird ProxyCommand re-prompts for
every channel, so multiplexing doesn't help):

```bash
/Applications/NetBird.app/Contents/MacOS/netbird ssh -u ubuntu ai-dev-server-jan-kubant 'echo ok'
```

**Permission for Claude.** Claude Code's auto-permission check blocks reading the
server's transcripts unless allowed. The repo's `.claude/settings.json` allowlists
`time-tracking/agent-sessions.sh`; to let Claude run ad-hoc `netbird ssh` too, add to
the **local, uncommitted** `.claude/settings.local.json`:

```json
{ "permissions": { "allow": ["Bash(/Applications/NetBird.app/Contents/MacOS/netbird ssh:*)"] } }
```

**Read the agent metadata** (worktree, branch, timestamps — never message content):

```bash
time-tracking/agent-sessions.sh 2026-09-14 2026-09-19 > ~/TimeTracking/agents.json
```

## Logging playbook (a week at a time)

1. `date` — confirm today (the clock/date has drifted during long sessions).
2. Last logged day: `status.py --date <day>` walking back (skill `clockify-day`).
3. Agents: `time-tracking/agent-sessions.sh <from> <to> > ~/TimeTracking/agents.json`
   (complete the NetBird login page when it opens).
4. Reconstruction: `time-tracking/aw-summary.py <from> <to> --agents ~/TimeTracking/agents.json`
   → active blocks (keyboard), calls, apps, branch titles, and per-block agent/worktree shares.
5. Calendar per day: `status.py --date <day>` (meetings; AW idle gap + calendar meeting = meeting).
6. Build entries: keep meetings (sized to the call / idle gap, not the calendar slot),
   split work around idle gaps (never bridge a break), label work blocks from the
   dominant agent worktree → `#<issue> <title>` (`gh issue view <n> --repo mild-blue/slp`),
   exclude personal worktrees (see `notes.md`).
7. Show the user the full entry list per day with totals; create only after explicit
   `create all` / numbers (skill Step 3–4).

## Retention / purge

ActivityWatch keeps history indefinitely by default. A purge script trims it:

- **Script:** `~/TimeTracking/aw-purge.py` — deletes events older than `RETENTION_DAYS`
  (default **30**) across all buckets via the local REST API. Supports `DRY_RUN=1` (count only).
- **Schedule:** LaunchAgent `~/Library/LaunchAgents/blue.mild.aw-purge.plist`
  (label `blue.mild.aw-purge`) runs it **daily at 03:30**; output logged to `~/TimeTracking/aw-purge.log`.

Change the retention window:

```bash
# edit RETENTION_DAYS in the plist (e.g. 7), then reload:
launchctl bootout   gui/$(id -u)/blue.mild.aw-purge
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/blue.mild.aw-purge.plist
launchctl kickstart gui/$(id -u)/blue.mild.aw-purge   # run once now
```

## Reconstructing a day ("what did I do today?")

Query the buckets at `localhost:5600` and aggregate by app / category (prefer aggregates over raw
titles), combine with local git activity, then draft entries via the `clockify-day` workflow.

```bash
# list buckets
curl -s http://localhost:5600/api/0/buckets/ | python3 -m json.tool

# events from a bucket (window / afk / vscode / web)
curl -s "http://localhost:5600/api/0/buckets/<BUCKET_ID>/events?limit=-1" | python3 -m json.tool
```

Example aggregation (time by app) is trivial: pull the `aw-watcher-window` events and sum
`data.duration` grouped by `data.app`.

## Known caveat: Rosetta 2 end-of-life

ActivityWatch v0.13.2 ships **Intel-only** binaries, so it runs through **Rosetta 2**. Apple is
phasing Rosetta out:

- **macOS 26 (Tahoe, current)** and **macOS 27 (Golden Gate, late 2026)** — Rosetta still works
  (macOS 26.4+ shows a one-time "Rosetta support will end" warning on launch — this is expected).
- **macOS 28 (fall 2027)** — Rosetta is generally removed; Intel-only apps stop working.

**Impact:** none until ~macOS 28. Before upgrading that far, switch to a native Apple-Silicon build
of ActivityWatch (the project is working toward `arm64` releases; build from source if needed) or
re-evaluate the tool.

## Uninstall

```bash
brew uninstall --cask activitywatch
launchctl bootout gui/$(id -u)/blue.mild.aw-purge
rm -rf ~/TimeTracking ~/Library/Application\ Support/activitywatch
# remove the ActivityWatch Login Item (System Settings > General > Login Items)
# remove the Web Watcher extension from Chrome/Brave
```
