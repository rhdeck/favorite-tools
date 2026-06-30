# Decisions

The decision log for `operating-model`. Newest-first. Each entry captures the
decision, a one-line rationale (the *why*, which is the expensive-to-reconstruct
part), and the date. A future agent reads this to avoid re-litigating settled
calls. Strategic "where we are" lives in the Notion Project Overview; technical
shape lives in [`ARCHITECTURE.md`](ARCHITECTURE.md); this file is *why it is the
way it is*.

---

## 2026-06-30

### Project Overviews DB + dual-write migration (#5, #16)
**Decision:** Add a Notion **Project Overviews** database (Name · Status ·
Repo · One-line purpose · Last externalized · Body) and give the Briefs DB a
**Project relation** to it. Migrate off the free-text `--project` tag via a
**dual-write** window: write both the relation and the legacy text property,
backfill, then rename `Project Overview` → `Project` and drop the text field.
**Why:** the free-text tag silently drifted (e.g. "Local AI Comparison" vs
"local-ai-comparison") and split history; making projects first-class with a
relation stops the fork, and dual-write makes the migration non-breaking for
in-flight briefs.

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
