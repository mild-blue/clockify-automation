# clockify-day skill

Logs today's Clockify time entries based on your Google Calendar. Claude proposes entries from your calendar events; you confirm; the create script writes them.

The skill itself is `SKILL.md` — this README is the one-time setup guide.

## Install

1. **Make the skill discoverable to Claude Code.** Either install it as a plugin/skill in `~/.claude/skills/clockify-day/`, or symlink:

   ```bash
   mkdir -p ~/.claude/skills
   ln -s "$PWD/skills/clockify-day" ~/.claude/skills/clockify-day
   ```

2. **Install Python dependencies** (use a venv if you prefer):

   ```bash
   pip install -r skills/clockify-day/requirements.txt
   ```

3. **Set the Clockify API key.** Get it in Clockify under Profile → Preferences → API, then copy the `.env` template and fill it in:

   ```bash
   cp skills/clockify-day/.env.example skills/clockify-day/.env
   $EDITOR skills/clockify-day/.env
   ```

   The scripts auto-load this file. (Plain `export CLOCKIFY_API_KEY=...` in your shell also works and overrides the `.env` value.)

4. **Set up Google Calendar OAuth** — see below.

## Google Calendar OAuth setup (one-time)

1. Go to <https://console.cloud.google.com/> and create a project (or pick an existing one).
2. **Enable the Google Calendar API**: APIs & Services → Library → search "Google Calendar API" → Enable.
3. **Configure OAuth consent screen** (Google moved this around — current path):
   - Left sidebar: **APIs & Services → OAuth consent screen** (in some projects it's now labeled **Audience**).
   - If it's the first time, click **Get started** / **Configure consent screen**.
   - **App information**: app name (e.g. `clockify-day`), user support email = your email. Click Next.
   - **Audience**: pick **Internal** (you have a Workspace org — only users in your org can use the app, no test users, no unverified-app warning). Click Next.
   - **Contact information**: your email. Click Next, agree, Create.
4. **Create OAuth client credentials**: APIs & Services → Credentials → Create Credentials → OAuth client ID → Application type **Desktop app** → name it (e.g. "clockify-day") → Create.
5. **Download the JSON** and save it as:

   ```
   skills/clockify-day/client_secret.json
   ```

6. The first run of `status.py` will open a browser window for the consent flow and write `token.json` next to `client_secret.json`. The token auto-refreshes; you only do the browser dance once. If it ever breaks (`invalid_grant`), delete `token.json` and rerun.

The required scope is `calendar.readonly`. The skill never modifies your calendar.

## Environment variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `CLOCKIFY_API_KEY` | yes | — | Clockify Profile → Preferences → API |
| `CLOCKIFY_WORKSPACE_ID` | no | user's `defaultWorkspace` | Set if you have multiple workspaces |
| `TIMEZONE` | no | `Europe/Prague` | IANA name; drives "today" |
| `WORKDAY_START` | no | `09:00` | Used to spot gaps |
| `WORKDAY_END` | no | `17:00` | |

## Usage

In Claude Code, just ask: "log my time", "doplň mi den", "what should I log today", "fill in my Clockify". Claude will run `status.py`, propose entries from your calendar, and ask for confirmation before calling `create.py`.

## Files

- `SKILL.md` — workflow Claude follows
- `scripts/status.py` — gathers Clockify state + calendar events
- `scripts/create.py` — writes confirmed entries to Clockify
- `.env` — your config (you provide; gitignored). See `.env.example`.
- `client_secret.json` — your OAuth client (you provide; gitignored)
- `token.json` — auto-created refresh token (gitignored)

## Privacy notes

- `client_secret.json` and `token.json` are credentials. Don't commit them. Don't paste their contents into chats.
- Time entry descriptions can be visible to managers/clients in Clockify reports — the skill is instructed to keep descriptions about the work, not attendee names or sensitive content.
- The skill never deletes or edits existing Clockify entries. Fix mistakes in the Clockify UI directly.
