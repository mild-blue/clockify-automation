# Logging notes

Rules and project-mapping conventions for this Clockify workspace. Claude reads this in **Step 2 — Reason** before proposing entries; rules here override generic guesses from `history`.

Most of this is distilled from the company Clockify manual (Mild Blue / slp.blue). Personal additions live alongside.

## SLP project breakdown

- **`slp`** — common to all clients. Dev, testing, release notes. Not tied to a specific client.
- **`slp - byznys`** — common to all clients. Contracts, faktury, konference, post-deployment biz (e.g. negotiating new features). May or may not be tied to a specific client.
- **`slp - support`** (no lab suffix) — bulk training (organizing or attending), webinars.
- **`slp - deployment (<lab>)`** — initial setup for a specific lab: data migration, deployment, initial training. Does NOT include biz to acquire the client — that's `slp - byznys`.
- **`slp - support (<lab>)`** — ongoing support for a lab once running: client tasks, comms, post-deployment training. In description, write the activity (e.g. "call") and the lab name when relevant.

When unsure between `slp` and `slp - byznys`: engineering/dev activity → `slp`, business/sales/contracts activity → `slp - byznys`.

## Activity → project

- **Standup (slp.blue)** → `slp`
- **Standup (internal)** → `internal`
- **1on1 / 1:1** → `internal`
- **Product sync, refinement, planning, retro (slp.blue)** → `slp`
- **Vibe coding** → `slp`
- **Hiring / interviews / pohovory** → `hiring`
- **Leadership meeting** → `internal`, description `Leadership`
- **NCLP cookies / cookie banner** → `slp - byznys` (compliance, not pure dev)
- **Business lunch** → `slp - byznys`
- **Cesta za klientem** → the relevant project (e.g. `slp - deployment (X)`), description `Cesta za klientem` + client name. Non-billable.
- **Administrativa / drobnosti** → `internal`
- **GitHub / Azure DevOps task** → repo's project, description `#123 TaskName`
- **Trello card** → described by card name; usually non-billable
- **Code review** → repo's project, description `review + krátký popis`
- **Hubspot pristupy / nastavovani** → `internal`
- **Ucetni firma** → `internal`
- **EFLM odpovedi / komunikace** → `internal`
- **Priprava na webinar** → `slp - byznys` (webinar = support/marketing, not pure dev)
- **Chatbot** (generic) → `slp` — see recurring-topics table for the specific issue
- **Pristupy do slp.blue pres VPN / SSH pristupy na instance** → `slp`
- **Onboarding noveho clena (uvodni schuzka, obedova diskuse)** → `internal`
- **Doporucujici hovor (reference call)** → `internal` unless clearly part of a hiring pipeline (then `hiring`)
- **Uklid issues / Uklid PRs / Prioritizace issues / drobne issue cleanup** → `slp`
- **Predani agendy (od kohokoli)** → `slp` when agenda is a slp.blue product area; `internal` if org-level handover
- **Call s Honzou (predavani sprintu, sync)** → `slp`
- **Byznys sync (obecny)** → `slp - byznys`
- **Marta Hynarova call (hiring)** → `hiring`
- **Marta o neshodach / Marta analyza agend** (compliance / requirements) → `slp - byznys`
- **Reseni s Tomasem / Diskuze o hiringu s Tomasem** → `hiring`
- **Priprava POC instance / Aktualizace POC instance / QMS instance vylepsene** → `slp - byznys` (POC/demo for prospects, not product dev)
- **POC Beckman & Roche (dev/discussion)** → `slp` (POC dev work, even when discussed with vendors)
- **Demo instance pro byzdev** → `slp - byznys`
- **Cesta do NCLP (meeting standards committee)** → `slp - byznys`
- **Cesta na vlak (uncategorised commute)** → `internal`
- **Isohelp meetings / schuzka Isohelp / isohelp** → `slp - byznys` (corrected 2026-07-23; earlier entries were `internal` and were moved)
- **Reseni newsletteru** → `internal`
- **Reseni 360 projekt / Shrnovani 360 / Hodnoty firmy** → `internal` (org-level projects)
- **Reseni teambuildingu** → `internal` (event organizing; can log full evening incl. cross-midnight if that's the reality)
- **Permissions setup pro X (Google Sheets, tools)** → `internal`
- **Reseni jak pristupit k AI / AI import / AI development** → `slp` when for slp.blue features; `internal` for tooling/access
- **AI jam (Mild Blue event)** → `internal`
- **Trh ceskych transfuznich laboratori / RTL Novartis projekt** → `byzdev/marketing`
- **LabMedAlliance (LMA) prep / demo** → `slp` (product-side demo instance work)
- **Business lunch with anyone (Tomasem, BC, klientem)** → `slp - byznys`, description `Business lunch s <name>`
- **Zapisy z 1on1 (writing 1on1 notes)** → `internal`
- **Discussion about a specific candidate (e.g. Viktor Holý, Marta Hynarova)** → `hiring`

### Recurring topics → stable GitHub issues (mild-blue/slp)

The user logs against the same issues repeatedly. When they say one of these phrases, map directly without re-searching (still confirm the issue is open if in doubt):

- **analyza rizik / diskuze nad riziky** → `#15133 Provest si analyzu rizik pro slp.blue v slp.blue`
- **MCP rizika / ovladani rizik** → `#15737 MCP: ovládání rizik, neshod a příležitostí ke zlepšení`
- **analyza NCLP** → `#15768 Analyza NCLP pomoci AI`
- **NCLP instance** → `#15474 NCLP instance POC`
- **zmenove protokoly** → `#12998 Agenda změnových protokolů`
- **MHT export/import** → `#15513 Fix export and import for MHT documents`
- **POC risk matrix / risk matice** → `#16005 POC risk matrix`
- **thready komentářů / inline comments / megaissue komentaru** → `#16145 Vytvořit thready komentářů`
- **Chatbot gateway POC / chatbot POC "contracts"** → `#15554 Chatbot gateway POC`
- **chatbot v slp.blue POC (generic "Chatbot POC")** → `#13921 chatbot v slp.blue POC` — this is the DEFAULT when the user just says "chatbot POC" without qualifier
- **chatbot voice mode / side banner** → `#16228 chatbot POC voice mode and side banner`
- **LabMedAlliance demo instance / LMA prep** → `#15966 LabMedAlliance demo instance`
- **SSH pristupy na nase stroje / pristupy na instance (ssh)** → `#15111 Bezpečnější SSH přístupy na naše stroje`
- **Sjednoceni pravidelnych akci pristroju / "regular actions in instruments"** → `#15210 Sjednoceni pravidelnych akci pristroju`

**Ambiguity tip**: when the user says just "chatbot" or "chatbot POC" with no gateway/voice/production qualifier, default to `#13921`. When they mention "gateway", "contracts", or working on the API surface — use `#15554`. When they mention "voice mode" or "side banner" — use `#16228`.

### Internal events (all → `internal`, all non-billable)

- **Friday Mild Blue lunch** — description `Lunch`, log only first **20 min**.
- **TechTalk (attending)** — description `TechTalk`, log only first **20 min**.
- **TechTalk přípravy / prezentace** — description `Příprava TechTalk` / `TechTalk prezentace`, log full time.
- **Mild Black** — log full time.

## Skip (don't track at all)

- Regular lunch / break
- Physical social events (hospoda, discgolf, grilovačka, …) — voluntary, untracked
- Out of office, transit, doctor, OOO

## Description style

- Be specific. Same activity → same name across days (consistency lets the script parse it).
- For meetings: include one of `call`, `meeting`, `schůzka`, `sync` in the description. Track real time spent, not calendar time. (A "meeting" that's really about one specific GitHub task → log it as the task, not as a meeting.)
- Deployment/support: don't repeat the client name in the description — it's in the project. Add lab name if there are multiple labs for the client.
- Business tasks for a specific client: include client name (or a clear partial / official abbreviation). Avoid nicknames and typos. Examples: ✅ `FN Ostrava`, `FNO`, `ostrava fn`. ❌ `Ostrava` alone (multiple clients there), `Thomayerka`.
- Czech without diacritics, terse.

## Phrasing the user uses

- **"do ted" / "doted" / "az do ted"** = up to the current clock time. Run `date '+%H:%M'` and use that as the end.
- **"pul na pul"** = split the block 50/50 between two activities.
- **Durations ("30 minut", "1 hour", "45 minut jeste")** are meant to fill into an open gap in the day — slot them into the nearest unlogged gap and confirm placement.
- **Standup** is logged ~09:25/09:30–10:00 even though the calendar event is shorter (09:30–09:50). Sometimes standup runs to 10:20 or 10:30 — take what the user says.
- **Working lunch**: a meeting can BE the lunch (e.g. "jednani jednatelu is lunch") — in that case don't add a separate lunch skip; the meeting entry covers the slot.
- **"9.7."** in Czech = July 9 (DD.MM. date format). Watch for this instead of a time.
- **"jeste rano tak hodinu" / "tak 30 minut"** = "also ~1h in the morning" / "~30 min" — the user is adding retroactive work into a gap, not giving a precise duration.
- **"predtim" / "potom" / "pak jeste"** = before / after / and also — refer to relative sequence around an anchor activity (usually standup or a calendar event).

## Workday shape

- **Start time varies**: 08:00, 08:30, 09:00, 09:30 are all normal starts. Don't assume 09:30.
- **Evenings**: chatbot POC, LMA prep, and #16068-style MCP work often happen 19:00–22:00 in a second block after a break.
- **Cross-midnight**: log entries that cross midnight as a single Clockify entry (`start` on day N, `end` on day N+1). Clockify accepts this. Used for teambuilding, late chatbot POC pushes.
- **Long days**: 10–14h logged days occur (esp. Wed / Mon with evening blocks). Don't cap or split "for the user's benefit."
- **Wednesday/Thursday** are often the heaviest days; **Monday** is sometimes a bank holiday — always confirm before backfilling.
- **Multi-day bulk logging**: the user often dumps 3–5 days of activities in one message; check `date` and split by day carefully, ask for the gap when unsure.

## Billable

- **Always billable** (set `billable: true` in the create payload):
  - Any `slp - deployment (<lab>)` project
  - Any `slp - support (<lab>)` project
- **Always non-billable** (default — `billable: false`):
  - `internal`, `byzdev/marketing`, `hiring`, `slp`, `slp - byznys`, `slp - support` (no lab suffix)
  - GitHub / Azure DevOps tasks (personal preference — overrides the manual's "typically billable")
  - Cesta za klientem
- Other projects (Trello cards, code review, planning, retro): non-billable unless explicitly told otherwise.

## Process / hygiene

- Ideal: start the timer when the task starts, stop when done. Second-best: enter retroactively with at least an estimate. Don't run a task for 2 seconds at the end just to "log it" — useless data.
- Tags are mostly unused now; only special ones like `out of scope` get used and the team agrees on them ad hoc.
- Closing: 1st–2nd of the month, sanity-check Clockify for missing description/project and duplicates. Jana builds attendance off this.

## ActivityWatch reconstruction (preferred over calendar-only)

The local ActivityWatch tracker is the primary signal for *what was actually
worked on*; the calendar only knows scheduled meetings. Full setup in
[TIME_TRACKING.md](../../../TIME_TRACKING.md) (server at `localhost:5600`).

- **Log daily.** AW purges after 30 days (03:30 daily). Reconstructing more than
  a few days from memory is where over/under-billing creeps in.
- **AW-first, calendar-second.** The richest signal is **VS Code window titles**
  (`aw-watcher-window`, app `Code`) — they carry the git branch + file + SSH host,
  e.g. `chatbot-legal-adr — email-ai-asistent.md — … [SSH: ai-dev...]`. The user
  works mostly in VS Code with Claude Code in the integrated **terminal**, so the
  window title is often the *only* signal (see below). Branches encode the task
  (`fix-16626-legacy` → issue #16626, `chatbot-legal-adr` → chatbot legal work),
  so read the branch to guess the task/project.
- **VS Code over SSH — the `aw-watcher-vscode` extension is mostly blind here.**
  It reports `file`/`project`/`language`, but only for files open on the machine
  where it runs; for Remote-SSH work it logs `unknown` unless the extension is
  installed **on the SSH host** too. So rely on the window title, which is set via
  `window.title` in VS Code settings to lead with `${activeRepositoryBranchName}`
  (configured 2026-09-11) — that puts the branch on every event, including when
  the terminal is focused and no editor is active.
- **Trim to active time.** Sum `aw-watcher-afk` `not-afk`; merge blocks with
  <15 min gaps; drop idle. Exclude personal browsing (Facebook, podcasts, maps,
  WhatsApp — often several hours of Chrome that must NOT be billed).
- **Never log through an idle gap.** A gap in `aw-watcher-afk` active time (no
  keyboard/mouse) is a break — lunch, errands, away — and stays **unlogged**,
  even when it falls in the middle of a task. **Split the work block around it;
  do not bridge it**, and do not extend a block past an idle gap just because the
  same task resumes after. (Learned the hard way: logging Nabidka straight
  through a 12:15–12:50 lunch the user had to correct.) Only exception is the
  calls/meetings rule below.
- **Calls/meetings override idle.** A span covered by the `aw-watcher-meet`
  bucket — or a clear off-keyboard idle gap that aligns with a calendar meeting —
  counts as a meeting (billable per the calendar), even though AFK shows idle and
  even if the call was in a background tab. Don't trim call time as a break.
  (A longer-than-scheduled meeting shows as a longer idle gap — size the entry to
  the gap, not the calendar slot.)
- **Confirm "today" first.** The machine clock/date can drift across a long
  session — verify with `date` before logging.

### Project mappings learned from AW file/branch signals
- `chatbot-legal-adr` branch (email-ai-asistent, analyza-pacientska-data,
  podklady-korespondence, DPA / VOP, AI-asistent emails) → `slp - byznys`
- Isohelp / acquisition letters (dopis-isohelp, acquisition-letter-analysis) → `slp - byznys`
- POC containers (`update-poc-containers.sh`), model benchmarking
  (`benchmark-*.pdf`, `run_benchmark`), STT/neshody audio, general slp dev → `slp`
- **Chatbot beta** (production-testing readiness) → `slp`, issue **#15805**

### Claude agent sessions on the dev server (task attribution)
The user works mostly through several parallel Claude Code agents on
`ai-dev-server-jan-kubant` (NetBird SSH), one **git worktree per agent**, often
sharing a branch — so the branch / VS Code title can't tell them apart. The
agents' transcripts can:

- Run `time-tracking/agent-sessions.sh <from> <to-exclusive>` (allowlisted). It
  prints metadata only — per session: worktree `cwd`, `branch`, timestamps. The
  first call per NetBird login opens a browser SSO page (the user completes it).
- **Worktree names carry the issue**: `17255-chat-image-poc` → #17255,
  `review-fix-17263` → #17263, `rebase-16977` → #16977, `legal-adr` → #16568,
  `nclp-skills-rebase` → #15768. Look titles up with `gh issue view <n> --repo mild-blue/slp`.
- Transcript "user" events include tool results, so agents produce timestamps even
  when the user is away. **Gate on AW AFK active time first**, then attribute each
  active block to the worktree with the most events inside it (top 1–2).
- VS Code window titles often just show whichever document was open (e.g. a DPA
  `.docx`) while the real work happened in an agent — prefer the agent signal.
- Worktrees outside `slp/` that aren't work (e.g. personal side projects) are not
  billable — ask the user once and exclude.

## Environment gotchas (this machine)

- The `.env` with `CLOCKIFY_API_KEY` lives in the **main repo copy** of the skill dir (`/Users/honza/Projects/clockify-automation/.claude/skills/clockify-day/.env`), NOT in worktree copies. Run scripts from the main-repo path.
- Sometimes `python` is not on PATH — the scripts require `requests` which lives in the conda env at `/opt/homebrew/Caskroom/miniconda/base/bin/python`. Fallback command:
  ```bash
  /opt/homebrew/Caskroom/miniconda/base/bin/python /Users/honza/Projects/clockify-automation/.claude/skills/clockify-day/scripts/status.py
  ```
- Clockify API sometimes times out (20s read timeout in scripts). Just retry — it usually works on the second attempt.
- When the shell `cwd` resets to a worktree, still invoke scripts by absolute path pointing at the main repo copy so `.env` loads correctly.

## Bulk-logging workflow tips

- When the user dumps many days at once, build **one combined JSON file** and call `create.py` once — much faster than day-by-day.
- Stage the file at `.cache/clockify_create_<yyyymmdd>_<label>.json` (repo-relative). The `.cache/` dir is gitignored.
- For crossing-midnight entries, put both `start` and `end` in the same JSON with correctly-dated ISO strings — no need to split.
- Billable flag matters only for `slp - deployment (<lab>)` and `slp - support (<lab>)` entries; set `"billable": true` in the JSON for those. Everything else defaults to non-billable and can be omitted.
