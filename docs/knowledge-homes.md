# Knowledge Homes

Where every fact lives, and why. This is the operational detail behind the four-homes grid in [operating-model.md](operating-model.md). The governing constraint is always the same: a substrate may hold knowledge only if it is **versioned + visible + cold-resumable**.

## The four homes

Knowledge sorts on two axes — **scope** (this project vs. how-we-operate) and **kind** (transient work vs. durable knowledge) — into four quadrants. Each has exactly one home. Nothing lives in two.

### 1. Project work → GitHub issues + PRs

What to do and what's decided, scoped to one project. Issues are the backlog and the decision record; PRs are the change record. This is where a graveyard shift reads its marching orders and writes its results. Visible (you watch the repo), versioned (issue history, PR diffs), cold-resumable ("get going on #N" is a complete handoff).

Issues carry a second job that falls out of the same substrate: they are also the **inter-project message bus.** Each project is an autonomous division whose orchestrator owns its own tree; the *only* sanctioned way for one project (or a coordination loop) to affect another is to **inject an issue into the target's repo**, which its orchestrator then adjudicates on its next shift — never to reach in and do the work directly. The same durable, versioned, visible artifact that is *your* backlog item is *another division's request to you*, handled the same way. Full protocol — the division boundary, loops-as-async-injection, and the worked example — in [coordination.md](coordination.md).

Two transient board states live inside this quadrant as labels — they are project-scoped work, not durable knowledge, and they disappear when the work resolves. They are siblings that together cover everything "in flight":

- **`observing` — landed-but-unproven.** A change that merged but isn't yet trusted: reopened with a named signal to watch and graduated after a quiet window. See the `observation-mode` skill. This is the *eval* substrate (watched-after-shipping).
- **`running` — executing-now.** A live cross-shift job still holding resources. See [the running register](#the-running-register-executing-now) below.

## The running register (executing-now)

The `running` register is the **executing-now** sibling of the `observing` register: one GitHub issue per **live cross-shift job** — a long-running or async process that outlives the moment it was launched (a multi-hour eval, a training run, a long migration, a remote agent, a background build, a queued job). It carries a **`running` label** and lives in the repo where the work runs. Its purpose is coordination across the shift boundary: a later shift or a live session must be able to see what is *still executing* so it doesn't collide with held hardware, re-run work already in flight, or misreport a still-running job as a decision awaiting the user.

**Why GitHub and not Notion.** A live job's liveness is *transient, project-scoped work* — the Project-work quadrant — and its home is therefore GitHub, the substrate the graveyard already sweeps at start of shift (so reading it costs nothing new). Notion Briefs is the *global time-series* home (progress across the business); a job may be *mentioned* in a brief, but its system of record is the GitHub issue, not the brief. The register satisfies the decisive rule: versioned (the heartbeat is the comment/edit history), visible (you watch the repo), cold-resumable (a fresh agent finds every live actor from `label:running` with zero transcript). One issue per job — mirroring `observing` (per-change, not a master list) — so each job carries its own heartbeat, its own close-with-result, and a clean per-job staleness signal.

**The entry shape** (a body a sweep can parse by eye):

```
Title:    [running] <one-line what — e.g. "Devstral vllm-mlx eval (dark-horse leg)">
Label:    running
- What:        what is executing and what question it answers
- Where:       host / harness (e.g. mac-studio, vllm-mlx) + how it was launched
- Holds:       the contended resource — e.g. "GPU: one big model resident"
               (the line a shift reads as occupied)
- Output:      path/artifact where results land
- ETA:         expected completion / progress N-of-M
- Reap:        how to check status and how to stop/clean it (PID, job id,
               `gh run watch`, queue id, screen/tmux target...)
- Heartbeat:   <timestamp> progress, last write, revised ETA   ← updated as it runs
```

**Lifecycle: register at launch → heartbeat while running → close on completion (noting the freed resource).** A heartbeat that goes stale past the threshold flips a sweep's read from "running, leave it alone" to "investigate — possibly dead": the same liveness logic as a brief stuck "In Progress" too long. Reaping is a human/agent decision (read `Reap`, confirm the job is actually dead, then close), never an automatic kill — the register is a *discipline* (you register at launch), not a process monitor or an enforced lock. "Holds: GPU" is a human-readable occupancy flag a sweep respects, not a mutex.

**Both shift modes read `running` first.** The `graveyard-shift` skill is the canonical reader (start-of-shift sweep + register-on-launch + reap). The `shift-change` skill is the second reader: it lists `running` jobs in its agenda compile as **in-flight actors with age — explicitly not as decisions awaiting the user** (a still-running eval is not a fork; misfiling it as one is exactly the noise shift-change strips). Together they keep both the autonomous and the live mode from colliding with, double-running, or misreporting a live job.

`running` is the complement to `observing`: together they answer "what's in flight" — `running` = *still executing, holding resources* (pre-completion); `observing` = *merged, watching a signal* (post-completion). They are genuinely different states, so they are distinct labels; conflating them would muddy both sweeps.

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
