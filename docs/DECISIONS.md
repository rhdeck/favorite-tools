# Decisions

The decision log for `operating-model`. Newest-first. Each entry captures the
decision, a one-line rationale (the *why*, which is the expensive-to-reconstruct
part), and the date. A future agent reads this to avoid re-litigating settled
calls. Strategic "where we are" lives in the Notion Project Overview; technical
shape lives in [`ARCHITECTURE.md`](ARCHITECTURE.md); this file is *why it is the
way it is*.

---

## 2026-07-01

### Project discovery is the read-side of coordination: the Overviews DB is the org chart, Briefs are the status wire
**Decision:** Make explicit — in [`coordination.md`](coordination.md) and pointed to from
[`CLAUDE.md`](../CLAUDE.md) — that reaching another division has a *read side* that
precedes the write side. There is **no hardcoded roster of projects**: you discover a
sister division by reading the Notion **Project Overviews DB** (the org chart — one page
per project, whose **Repo field is the division's address**) and its recent **Briefs**
(the status wire — current state, is-it-active), then message it by injecting a GitHub
issue into that repo. A **blank Repo field is a routing failure**, not a cosmetic gap — a
division with no address cannot be reached. `overview list` enumerates the roster.
**Why:** the coordination canon (the entry below) specified *how to affect* another
project (inject an issue) but not *how to become aware of* one or *how to find its
address*. Without the read side, the write side has nowhere to send to — and the sc-auth
orphan (blank Repo) showed a real division that had literally become unaddressable. Naming
the two Notion DBs as the live registry (rather than any static list) keeps discovery on
substrates the model already maintains, and reframes the Overview Repo field as
load-bearing routing infrastructure. Shipped into observation as reversible doc canon.

### Inter-project coordination protocol: GitHub issues are the cross-project message bus
**Decision:** Adopt as canon that **each project/repo is an autonomous division
with its own orchestrator**, and the **only** sanctioned way for one project (or a
coordination loop) to affect another is to **inject a GitHub issue into the
target's repo** — the target's orchestrator then considers it and decides how (or
whether) to bring it to bear on its next shift. Outsiders never reach into a
division's repo and do the work themselves. This **extends the four-homes rule**
("GitHub issues = project work") into "issues are also the inter-project message
bus / async RPC between autonomous agents." **Corollary on loops:** recurring
coordination is expressed as loops that **inject durable issues** into target repos
for async pickup by each target's shift — *not* as synchronous triggers that drive
another project's agent to do X now. Captured as new prose canon in
[`coordination.md`](coordination.md), pointed to from [`operating-model.md`](operating-model.md)
and [`knowledge-homes.md`](knowledge-homes.md) (§1), with the operational half folded
into the `graveyard-shift` skill.
**Why:** the model is proving out across ~10 projects and needs a scaling story for
coordination that doesn't collapse the division boundary or trap coordination in a
live, in-memory trigger. An injected issue is versioned + visible + cold-resumable
(the decisive rule); a synchronous trigger is none of those and bypasses the one
actor — the target's orchestrator — that holds the division's full context. Making
the issue the async message decouples requester from executor and is what lets the
whole system run asynchronously at each division's own cadence. The Project
Overviews rollout is the first worked instance: ~10 projects filled their **own**
overviews via an injected `graveyard-infra` fill-issue per repo, not centrally —
this protocol already in action (see the atomicity entry below). Shipped into
observation as reversible doc/skill canon.

### Seeding a Project Overview page and injecting its fill-issue must be atomic
**Decision:** Creating a Notion **Project Overview** page for a project and
injecting that project's canonical fill-issue into its repo are **one
indivisible step** — never one without the other. The invariant: *an overview
in an unfilled state with no open fill-issue in its repo is an orphan bug; so is
an open fill-issue with no page.* The `setup-graveyard-project` skill now carries
the atomicity rule, the canonical fill-issue template (title + verbatim body), a
standardized **`graveyard-infra`** label on the fill-issue so cross-repo audits
query by label instead of grepping titles, and a documented orphan-audit
procedure (reconcile `overview list` unfilled pages against open fill-issues per
repo). `notion-briefs` and `graveyard-shift` cross-link to the procedure; a
follow-up issue proposes an `overview audit` CLI command to automate it.
**Why:** a bulk seed created overview pages for projects that never got a driving
fill-issue — producing **orphan pages that can never self-fill** (sc-auth,
sc-kg-analysis/"State Change Mentor", and thedebate/"Councilors" each had a page
with zero fill-issue; all three were repaired by hand). Page-creation and
issue-injection were not atomic, so the setup flow could silently manufacture
orphans. Making the two a single step — and giving the audit a label to query —
closes the gap durably. Shipped into observation as reversible doc/skill canon.

### Capture the north-star vision in `docs/VISION.md`
**Decision:** Add a vision document that states where the model is *heading*,
sitting above the constitution (which states what it *is*). Core frame: the model
is about **how to work — and run a business — in the age of AI**, where AI
occupies the **liminal space between delegation (to humans) and automation (to
tools)** and must be managed as neither. "Graveyard" names the biggest idea *so
far*, not the ceiling (parallel: Skills Manager → OS Manager grew past its
name). Trajectory: from tech work → to an **idea business** whose manifestations
are **software, content, and services**, with AI at their intersection — which is
why content is canon here, not just code. The doc is explicitly **emerging, not
doctrine**; the constitution/skills still win on concrete rules.
**Why:** Ray articulated a vision materially larger than the graveyard mechanism
and asked to memorialize it here so the direction is durable and visible, not
trapped in a transcript. Capturing it prevents future agents (and future Ray)
from mistaking the current biggest idea for the whole model. Shipped into
observation — a living document expected to be corrected as the model grows,
not a finished spec.

### The operating model covers CONTENT, not just code — `essay-workshop` + `avoid-ai-voice` are canon
**Decision:** The operating model is not code-only. Managing the **content
pipeline** is part of how the business works, and its skills live here as
first-class canon: **`essay-workshop`** (capture → workshop → publish essays and
mental models through the State Change Notion pipeline) is the content
counterpart to `notion-briefs` — same "how we manage a pipeline in Notion" shape,
pointed at content instead of code/briefs. **`avoid-ai-voice`** is the voice
guardrail on that pipeline. Both are committed to `skills/`.
**Why:** Ray placed both skills in this repo deliberately. Everything the model
had covered so far manages *code* (issues, PRs, shifts, reviews); content is an
equally load-bearing axis of the business and belongs in the same operating
model. **Corollary for agents:** when new files appear in this repo, treat them
as intentional — Ray's placement *is* the intent. Do not "clean up," relocate, or
second-guess additions as stray; that is overstepping (an agent moved these two
out on a distribution-cleanliness guess — wrong). Read new material as canon to
integrate, not drift to reconcile.

## 2026-06-30

### Vendor `credit-pacing` into the repo — complete the executable canon
**Decision:** Copy the `credit-pacing` skill from the global `~/.claude/skills/`
into `skills/credit-pacing/`, and list it (plus the already-vendored
`observation-mode`) in the README skills table. The graveyard-shift and codex-pr
canon reference `credit-pacing` as load-bearing (budget-gate every fan-out wave,
turn "pause" into "gate one path, keep working"); it was the last such skill
still living only as a global skill, not in-repo. Same move #15 made for
`observation-mode`.
**Why:** the model's executable canon must travel with the repo. A cold clone
(including one handed to another machine or a partner) that references
`credit-pacing` but doesn't contain it isn't a complete, resumable operating
model. Vendoring closes the gap so `git clone` + the Notion Overview is the whole
system. (Two non-model skills — `avoid-ai-voice`, `essay-workshop` — that had
drifted into the working tree were relocated back to global skills, not
committed: they're personal/generic, not the operating model, and must not ship
in a partner-facing repo.)

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
