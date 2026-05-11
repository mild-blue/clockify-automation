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
