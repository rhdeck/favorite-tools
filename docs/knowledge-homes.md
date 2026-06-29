# Knowledge Homes

Where every fact lives, and why. This is the operational detail behind the four-homes grid in [operating-model.md](operating-model.md). The governing constraint is always the same: a substrate may hold knowledge only if it is **versioned + visible + cold-resumable**.

## The four homes

Knowledge sorts on two axes — **scope** (this project vs. how-we-operate) and **kind** (transient work vs. durable knowledge) — into four quadrants. Each has exactly one home. Nothing lives in two.

### 1. Project work → GitHub issues + PRs

What to do and what's decided, scoped to one project. Issues are the backlog and the decision record; PRs are the change record. This is where a graveyard shift reads its marching orders and writes its results. Visible (you watch the repo), versioned (issue history, PR diffs), cold-resumable ("get going on #N" is a complete handoff).

### 2. Global work → Notion Briefs DB

Progress and time-series across the whole business — shift reports, briefs, plans — for *every* project, newest-first, tagged by project. This is the cross-project log of what's moving. Published via the `notion-briefs` CLI; never a local `test-plans/*.md` file.

### 3. Project durable knowledge → repo docs **+** Notion Project Overview

This quadrant has **two** homes on purpose, because it serves two different readers. This is the refinement that the rest of this doc turns on — see the next section.

### 4. Global durable knowledge → skills + global `CLAUDE.md`

How we operate, everywhere: the executable procedures (skills) and the standing operating principles (global `CLAUDE.md`). Not project-specific. Versioned in git, visible, and loaded into every session by construction.

## Two flavors of project source-of-truth

A project has **two canonical "what is true" surfaces, for two readers**. They must not duplicate.

| | **Repo docs** | **Notion Project Overview** |
|---|---|---|
| Reader | an **agent**, to execute | a **human**, to re-orient |
| Holds | technical canon — architecture, decisions, conventions, hazards | strategic state — what the project is for, where thinking is "from the point of view of State," why it exists |
| Shape | code-shaped, diffable, PR-reviewed | not code-shaped; prose, human-facing |
| Versioned with | the code | Notion page history |

**The discipline:** the Overview holds *strategic state* and **points to git for technical canon — it never copies it.** One source of truth per fact, cross-linked. The moment the Overview restates an architecture detail that lives in `docs/ARCHITECTURE.md`, you have two homes for one fact and they will drift. The Overview says "the architecture canon is in the repo" and links; it spends its own words on the *why* and *where-we-are* that no code file should carry.

## The minimal graveyard-ready repo contract

To be graveyard-managed, a repo must carry at minimum:

- **`CLAUDE.md`** — agent operating instructions / the entry point to technical canon.
- **`docs/OVERVIEW.md`** — one-line purpose + a link to the Notion Project Overview. It *points out, never duplicates.*
- **`docs/DECISIONS.md`** — the decision log.
- **`docs/ARCHITECTURE.md`** — the architecture canon.

That is the floor, not the ceiling. A project with these four files and a current Notion Overview is resumable by a cold agent; one missing them is not.

## The Project Overviews DB

The Notion Project Overview pages are themselves a database, so projects are first-class and inventoried. Each project is a page with:

- **Name**
- **Status** — Inception / Graveyard / Paused / Done
- **Repo** — URL
- **One-line purpose**
- **Last externalized** — a date, which doubles as an *integrity check*: a stale date means the durable state has fallen behind reality.
- **Body** — strategic state + links (out to git for technical canon).

The Briefs DB gains a **Project relation** to this DB, so progress over time (Briefs) connects to standing strategic state (Overviews).

## The anti-pattern: local memory as a shadow knowledge base

This is the cautionary tale the whole model is built to prevent.

In **Skills Manager**, roughly **16 local agent-memory files** had quietly accumulated. Individually each looked harmless — a note here, a context dump there. Collectively they had become a **parallel, invisible knowledge base**, overlapping what already lived in GitHub and Notion. Three failures at once:

- **Not versioned** — no diff, no review, no trustworthy history.
- **Not visible** — Ray never saw them, so they could contradict the visible record and no one would know.
- **Not cold-resumable** — they lived beside one agent's working context, not in the system of record, so a fresh agent couldn't find or trust them.

The damage is not the files themselves; it's that they become a *second source of truth* that silently competes with the real one. An agent reading the memory file and an agent reading GitHub now believe different things about the same project.

**The rule that follows:** durable project knowledge is externalized to **git / Notion, never local memory.** Local memory is demoted to a **thin accelerant** — a scratchpad that speeds one agent's current task — and for a mature project it should trend toward **zero**. If something in local memory is load-bearing, that is a bug: it belongs in a repo doc or the Notion Overview, and the fix is to move it there and delete the local copy.
