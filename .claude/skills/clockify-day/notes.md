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
- **Isohelp meetings / schuzka Isohelp** → `internal`
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
