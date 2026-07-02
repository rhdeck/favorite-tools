# CLAUDE.md — operating instructions for `operating-model`

The first thing a cold agent reads here. This is the **technical-canon index +
rules of the road** for working in this repo. It points into the canon; it does
not restate it.

## What this repo is

`operating-model` is the operating system for the **graveyard way of working** —
building big things with autonomous overnight agent shifts that *compound*
because every load-bearing fact is externalized into a substrate that is
**versioned + visible + cold-resumable** (git and Notion), never trapped in a
chat transcript or a local memory file. This repo is not a tool bag and not an
application: it is **prose canon** (the principles) plus **executable canon**
(the skills that enact them). There is no build, no test suite, no runtime.

**Current phase: Graveyard.** This repo satisfies its own minimal
graveyard-ready contract (the four files below) and is driven from its GitHub
issue backlog. It dogfoods the model it defines.

## Where knowledge lives (read these before acting)

- **`docs/VISION.md`** — the north star: where the model is *heading* (a
  management model for AI in the liminal space between delegation and
  automation; an idea business whose manifestations are software, content, and
  services). Read for direction; it's emerging, not doctrine.
- **`docs/operating-model.md`** — the constitution: thesis, the two-axis /
  four-homes grid, the versioned-visible-cold-resumable rule.
- **`docs/lifecycle.md`** — the three phases and why the externalization event
  is the whole game.
- **`docs/knowledge-homes.md`** — the four homes in depth, the repo contract,
  the local-memory anti-pattern.
- **`docs/coordination.md`** — inter-project coordination: how you **discover**
  sister divisions (read the Notion Project Overviews DB — the org chart, with
  each project's repo as its address — and the Briefs DB — the status wire) and
  how you **reach** them (the only sanctioned way for one project to affect
  another is to inject a GitHub issue into its repo; issues are the cross-project
  message bus, and loops become async issue-injection, not synchronous triggers).
- **`docs/DECISIONS.md`** — the decision log: *why* things are the way they are.
  Read it before re-opening a settled call.
- **`docs/ARCHITECTURE.md`** — what the system is and how the pieces fit.
- **`docs/OVERVIEW.md`** — one-line purpose + link to the Notion Project
  Overview (strategic, human-facing state). Points out; never duplicates.

## How the publisher CLI integrates

The Notion bridge is a **separate, project-neutral** tool at
`~/.config/ai-briefs/notion_briefs.py` (not in this repo; shared across all
projects). Use it to land knowledge in Notion:

- **Briefs / shift reports / plans** → the Briefs DB:
  `python3 ~/.config/ai-briefs/notion_briefs.py publish --project "Graveyard Operating Model" --title ... --type ... --status ... --file ...`
- **Strategic state for this project** → the Project Overviews DB:
  `python3 ~/.config/ai-briefs/notion_briefs.py overview upsert --name "Graveyard Operating Model" ...` (idempotent).

Run it from inside this repo so GitHub refs auto-link and the git remote is
detected. Config (`token`, `config.json`) lives in `~/.config/ai-briefs/` and is
environment-specific — never commit it. If the tool isn't configured here, run
the `notion-briefs` setup skill. Full flags: that directory's `README.md`.

## Conventions and guardrails

- **One source of truth per fact.** The *why* lives in `docs/` (prose), the
  *how* lives in `skills/` (procedures), strategic state lives in the Notion
  Overview, work lives in GitHub issues/PRs. Docs cross-link; they never
  duplicate. If you find yourself pasting architecture into the Overview, or a
  decision into two files, stop — pick the one home.
- **No local memory as a source of truth.** Local agent-memory files
  (`.memory`, `CLAUDE.local.md`, scratchpad notes) are a thin accelerant at
  most, trending to zero. Anything load-bearing goes to its durable home (repo
  docs / Notion / an issue), then the local copy is cleared. A load-bearing
  fact found only in local memory is a bug.
- **Project name is "Graveyard Operating Model"** for both Briefs and the
  Project Overview — match it exactly, the publisher auto-registers typos as new
  projects and splits history.
- **Observation-first.** Ship canon/skills into a watched observation phase
  rather than blocking PRs until provably perfect; iterate from signals. See the
  `observation-mode` skill.

## How to work here

- The backlog is the GitHub issues on `rhdeck/operating-model`. A graveyard
  shift drains it directly; `gh issue list --state open` is the marching order.
- **Need to coordinate with another project (line of business)?** Discover it via
  the Notion Project Overviews (`notion_briefs.py overview list`) + its recent
  Briefs, then affect it *only* by injecting a GitHub issue into the repo named
  on its Overview — never by editing its tree yourself. Full protocol:
  [`docs/coordination.md`](docs/coordination.md).
- Edits are docs + skills, so review is human/judgment review, not tests. Open a
  real PR (the `codex-pr` or `pr-package` skills), surface load-bearing calls,
  merge into observation.
- When durable knowledge accumulates from a live session, re-run
  `setup-graveyard-project` to re-externalize and re-stamp **Last externalized**
  on the Overview.
