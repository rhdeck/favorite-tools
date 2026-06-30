# Decisions

The decision log for `operating-model`. Newest-first. Each entry captures the
decision, a one-line rationale (the *why*, which is the expensive-to-reconstruct
part), and the date. A future agent reads this to avoid re-litigating settled
calls. Strategic "where we are" lives in the Notion Project Overview; technical
shape lives in [`ARCHITECTURE.md`](ARCHITECTURE.md); this file is *why it is the
way it is*.

---

## 2026-06-30

### The running register — track cross-shift live jobs on a `running` label (#13)
**Decision:** Add the **running register** as model doctrine: the *executing-now*
sibling of the `observing` register. Substrate is a **GitHub `running` label,
one issue per live cross-shift job**, in the repo where the work runs —
registered at launch, heartbeated while executing, closed (reaped) on completion
noting the freed resource. The graveyard sweeps `gh issue list --label running`
at start of shift (held resources / live actors — don't collide, don't re-run,
don't misreport a still-running job as a decision) alongside the existing
stale-draft + `observing` sweeps. Documented the entry shape (What / Where /
Holds / Output / ETA / Reap / Heartbeat) and lifecycle in
[`knowledge-homes.md`](knowledge-homes.md). Rejected alternatives: **Notion**
(that's the *global time-series* home — wrong quadrant for transient
project-local liveness, and it splits the job from the issues a shift already
sweeps) and a **single rolling register issue** (loses per-job heartbeat and
staleness; one-issue-per-job mirrors `observing`). A *new* label, not reused
`observing`, because they're different states: `running` = still executing,
holding resources (pre-completion); `observing` = merged, watching a signal
(post-completion).
**Why:** a long-running job (eval, training run, remote agent, build) can
outlive the shift that launched it and was previously invisible to the board —
the live trigger was a Devstral vllm-mlx eval holding the GPU with no GitHub
record (rhdeck/local-ai-comparison#37), which a later shift could blindly
collide with. Liveness is transient, project-scoped *work*, which the four-homes
model puts in GitHub — and the graveyard already sweeps GitHub at start of
shift, so the read costs nothing new. It's a discipline (register at launch),
not a process monitor or an enforced lock; auto-detection of orphans and
real resource leases are explicitly out of scope.

### Instrumented-signal gate: observation eligibility raised from *nameable* → *instrumented* (#15)
**Decision:** Vendor the `observation-mode` skill into this repo (`skills/observation-mode/`)
and raise its observation eligibility gate #2 from **nameable** to **instrumented**.
The observation contract's "Where it'd show" beat becomes a required **Signal source**
field with three parts — the production **artifact** that records the signal, the
literal **query** that reads it, and the **threshold** that separates healthy from
regressed. The shipping PR must *build* that signal source (a log line/counter that
doesn't exist yet is added in the same diff); a signal the PR can't make queryable is
**not** observation-eligible and falls back to prep/proposal. The graveyard sweep now
**runs the query and records the dated reading** on the issue, so graduate-vs-regress
is evidence-backed, not a vibe check. **Carve-out:** non-instrumentable work
(planning/eval/doc/copy issues with no production signal) keeps a concrete **non-code**
signal source (a user-report channel, a "no follow-up issue filed in 14d" check) — the
gate forces *concreteness of where-to-look*, not a code metric in every case, and does
not manufacture metrics for trivial changes whose revert is free.
**Why:** *nameable ≠ queryable.* A prose "watch for X" passes the old gate but leaves
no artifact a later shift can actually read, so the sweep degrades to re-deriving the
concern and guessing — the contract *looks* filled in but can't be evaluated, which makes
the observation window decorative. Making the read/observability slice a build-time
deliverable of the shipping PR keeps the loosened ship-bar honest: shipping-into-observation
costs a small instrumentation slice up front and buys a real eval in return. (Cost is a
`grep`-able log line, not a metrics framework.)

### This repo IS the operating model; the work is improving it (docs + skills)
**Decision:** Drop the "favorite-tools split" framing (closed #8). This
repository is *the operating model* — its purpose is to hold and improve the
model, expressed as documents, skills, and harness files. The work here is
**model alteration, not feature code**: issues and conversation evolve the
model; shifts express those changes as edits to `docs/` and `skills/`. Whether
to share the model more broadly (a separate *public* tools repo, later) is a
downstream concern that does not shape this repo now (parked as #19).
**Why:** focusing on "what to share" diluted the actual job. Naming this *the
operating model* and keeping attention on making it good is what creates the
value; packaging for others is only worth doing once the model is strong.

### operating-model is the model; skills-manager is the interface
**Decision:** Keep two repos with distinct jobs and never conflate them.
`operating-model` is *what the model is* — the canon/principles, where decisions
about how graveyard-shift work works get made. `skills-manager` is *the
interface / supporting software* through which we discover, review, modify, and
(most importantly) **reference** that model from real projects — beyond the
Ray↔Claude chats. skills-manager is a lens + workflow over the git canon, never
a divergent copy. Tracked in skills-manager #101 (epic) + #102–105.
**Why:** the model is proving out across 10 projects; it can't keep evolving
only in chat transcripts. The interface scales discovery/review/decision and
turns the principles into infrastructure projects cite — but only if the
"what it is" stays the single source of truth and the "how we work it" lives
separately, so the two don't drift into competing canons.

### Project Overviews DB — relation replaces the free-text tag (#5, #16)
**Decision:** Add a Notion **Project Overviews** database (Name · Status ·
Repo · One-line purpose · Last externalized · Body) and link each brief to it
via a single **`Project Overview` relation**. The free-text `--project` tag was
**removed entirely** (not renamed): all 73 existing briefs were backfilled onto
the relation, the `local-ai-comparison`/`skills-manager` forks collapsed, then
the legacy text property was dropped. `overview upsert` also gained
`--icon`/`--cover`.
**Why:** the free-text tag silently drifted (e.g. "Local AI Comparison" vs
"local-ai-comparison") and split history; making projects first-class with a
clickable relation stops the fork and lets every brief link into a real project
page. (Superseded the original dual-write-then-rename plan — Ray chose to retire
the tag outright once backfill was clean.)

### Minimal graveyard-ready repo contract
**Decision:** A repo is graveyard-ready iff it carries **four** files:
`CLAUDE.md`, `docs/OVERVIEW.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`
(plus a current Notion Project Overview). No partial credit.
**Why:** this is the floor that makes "clear the session and resume from disk"
a true statement — a cold agent with only `git clone` + the Notion Overview can
resume; missing any of the four and it starts blind.

### `externalize-project` → `setup-graveyard-project` rename (#3)
**Decision:** Rename the skill to `setup-graveyard-project`; keep the concept
verb **"externalization"** for the *event* it performs. It is a standalone
skill, not a section inside `graveyard-shift`.
**Why:** the trigger and moment are distinct ("make this project
graveyard-ready"), and the skill name should match how a user reaches for it,
while the noun "externalization event" stays as the name of the ceremony in the
canon.

### Observation-first philosophy (#1, #3, #15, observation-mode skill)
**Decision:** Ship canon and skills **into observation** rather than blocking
PRs until provably perfect. Merge, then reopen/label for observation with a
named signal to watch, and iterate from real signals.
**Why:** this work is judgment-shaped and can't be red/green-tested; shipping
into a watched window lets us ship *more* and catch regressions as regressions,
instead of stalling on pre-merge certainty we can't actually obtain.

## 2026-06-29

### Dogfood: externalize operating-model on itself (#12)
**Decision:** Run `setup-graveyard-project` on this repo as its first real
dogfood — produce the four contract files and a Notion Overview here.
**Why:** the canon defines the contract but the repo didn't satisfy it; a model
that can't externalize itself has no standing to ask other projects to.

### Smart routing renamed and parked someday (#6)
**Decision:** Rename "TAGS" → **smart routing** (route work across agent/model
tiers by task) and park it at `priority:someday`. Revisit when the token-price
differential across model tiers widens enough to justify the orchestration
complexity.
**Why:** most of the mechanics already exist in `graveyard-shift` +
`credit-pacing` + `codex-pr`; the only genuinely new piece is deliberate
cost-tiering, whose payoff is edge-case today and bets on a price spread that
hasn't arrived yet.

### favorite-tools split recommendation (#8 — proposed, pending Ray)
**Decision (proposed, not executed):** Eventually carve a separate **public
`favorite-tools`** repo for genuinely redistributable skills (`codex-pr`,
`research-brief`), leaving the operating-model machinery (`graveyard-shift`,
`setup-graveyard-project`, `notion-briefs`, `shape-an-epic`, `pr-package`)
here. **Defer the actual file split** until the docs/ canon (#1) and
`setup-graveyard-project` (#3) land.
**Why:** the model-vs-tool line answers itself per skill only once the canon
exists; splitting earlier is guessing. This remains pending Ray's go.

## 2026-06-28

### Repo renamed favorite-tools → operating-model
**Decision:** Rename `rhdeck/favorite-tools` → `rhdeck/operating-model`; public
for now, private later.
**Why:** the repo is the **operating model** for building with graveyard
shifts, not a tool bag — the name should state what it is.

### Canon home = the `docs/` directory
**Decision:** The human-readable constitution lives in `docs/`
(`operating-model.md`, `lifecycle.md`, `knowledge-homes.md`); the `skills/`
directory is the executable canon. Docs cross-link skills and never duplicate
them.
**Why:** one source of truth per fact — the *why* lives in prose under `docs/`,
the *how* lives in procedures under `skills/`, and keeping them separate but
linked stops the two from drifting.
