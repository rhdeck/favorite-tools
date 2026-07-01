# Architecture

What `operating-model` is and how its pieces fit. This describes what *is* now,
not aspirations (those are GitHub issues). The *why* behind these choices is in
[`DECISIONS.md`](DECISIONS.md); the strategic "where we are" is in the Notion
Project Overview linked from [`OVERVIEW.md`](OVERVIEW.md).

## What this is

`operating-model` is the operating system for the graveyard way of working: a
method for building big things with autonomous overnight ("graveyard") agent
shifts that compound, because every load-bearing fact is externalized into a
substrate that is **versioned + visible + cold-resumable** (git and Notion),
never trapped in a chat transcript or a local memory file.

It is **not a software application** — there is no build, no test suite, no
runtime. The repo is two kinds of artifact: **prose canon** (what we believe)
and **executable canon** (the procedures that enact it).

## The three pieces and how they fit

```
   docs/  ── human-readable constitution (the WHY)
     │            cross-links, never duplicates
     ▼
  skills/ ── executable canon (the HOW: procedures an agent runs)
     │            skills call out to ↓
     ▼
  ai-briefs publisher  ── the Notion bridge
  (~/.config/ai-briefs/notion_briefs.py, a separate cross-project tool)
     ├── Briefs DB            (time-series: shift reports, briefs, plans)
     └── Project Overviews DB (standing strategic state, one row per project)
```

### 1. `docs/` — the constitution (prose canon, the WHY)

Human-readable principles. These say *why*; they point at skills for *how* and
never restate them.

- [`operating-model.md`](operating-model.md) — the thesis, the two-axis /
  four-homes grid (scope × kind), and the decisive rule: *a substrate may hold
  knowledge only if it is versioned + visible + cold-resumable.*
- [`lifecycle.md`](lifecycle.md) — the three phases (inception → the
  externalization event → the graveyard phase) and why the externalization
  event is the whole game.
- [`knowledge-homes.md`](knowledge-homes.md) — the four homes in depth, the two
  flavors of project source-of-truth (repo docs for agents, Notion Overview for
  humans), the minimal graveyard-ready repo contract, and the local-memory
  anti-pattern.
- [`coordination.md`](coordination.md) — inter-project coordination: each project
  is an autonomous division; the only sanctioned way for one to affect another is
  to inject a GitHub issue into its repo (issues are also the cross-project
  message bus), and loops become async issue-injection, not synchronous triggers.
- [`OVERVIEW.md`](OVERVIEW.md), [`DECISIONS.md`](DECISIONS.md), this file — the
  repo's own contract artifacts (it dogfoods the contract it defines).

### 2. `skills/` — executable canon (the HOW)

Each skill is a directory with a `SKILL.md`. They are the procedures the model
runs; the docs are the principles those procedures serve. Two groups:

- **Operating-model machinery** (these *are* the model):
  - `graveyard-shift` — drain the open issue backlog autonomously off durable
    state; the core working loop everything else serves.
  - `setup-graveyard-project` — the ceremony that performs the externalization
    event (lifecycle step 2): backlog → issues, technical canon → repo docs +
    `CLAUDE.md`, strategic state → Notion Overview.
  - `notion-briefs` — set up / repair the shared cross-project Notion Briefs
    system in a new environment.
  - `shape-an-epic` — turn an underspecified issue into a concrete proposal.
  - `pr-package` — open a PR as a decision package with load-bearing calls
    surfaced.
- **Redistributable tools** (useful to anyone; candidates for the public
  `favorite-tools` split, #8):
  - `codex-pr` — create a PR, review with `codex review` in a loop until clean,
    auto-merge.
  - `research-brief` — produce a skimmable research/analysis markdown brief.

### 3. The ai-briefs publisher — the Notion bridge

A **separate, project-neutral** CLI at `~/.config/ai-briefs/notion_briefs.py`
(stdlib only, no pip deps; lives outside this repo so every project shares it).
Skills here call it to land knowledge in Notion. It manages two databases:

- **Briefs DB** — time-series of shift reports, briefs, and plans across all
  projects, newest-first, tagged by project. (`publish`/`append`/`set-status`.)
- **Project Overviews DB** — one row per project carrying standing strategic
  state: Name · Status (Inception/Graveyard/Paused/Done) · Repo · One-line
  purpose · **Last externalized** (date, doubling as an integrity check) ·
  Body. (`overview upsert`/`overview list`.) The Briefs DB has a **Project
  relation** to this DB so progress-over-time connects to standing state.

Config lives in `~/.config/ai-briefs/` (`token` chmod 600, `config.json` with
the DB ids) — never committed, environment-specific. See that directory's
`README.md` for command/flag detail.

## The key boundary

The two **project** durable-knowledge homes serve different readers and must
never duplicate:

- **Repo docs** (`CLAUDE.md` + `docs/`) = technical canon an **agent** reads to
  execute. Code-shaped, diffable, PR-reviewed, versioned with the repo.
- **Notion Project Overview** = strategic state a **human** reads to re-orient.
  Prose, human-facing. It **points to git for technical canon; it never copies
  it.** `docs/OVERVIEW.md` is the thin in-repo pointer to that page.

When unsure where a fact goes: *would an agent need it to execute?* → repo docs.
*Would a human need it to decide whether to re-engage?* → the Overview. *Is it a
unit of work?* → a GitHub issue.
