# The Graveyard Operating Model

This is the constitution. It states *why* this repo exists and the one rule everything else follows from. The skills under [`skills/`](../skills) are the executable canon — the procedures an agent runs. These docs are the human-readable canon — the principles those procedures serve. They cross-link; they never duplicate.

## Thesis

**Big things get built by autonomous graveyard shifts running off durable, visible state — not by knowledge trapped in a chat transcript or a private memory file.**

A graveyard shift is an agent doing real work while you sleep. For that to compound instead of evaporate, every project must externalize what it knows into substrates that are **versioned, visible to you, and resumable cold**. A shift that ends with its context only in a transcript has built nothing durable — the next agent starts blind.

Local, per-project agent memory fails all three tests. It is not versioned (no diff, no review, no history you trust), not visible (you never see it), and not cold-resumable (it lives beside one agent's worktree, not in the system of record). So it must be **demoted from a source of truth to a thin accelerant** — ideally close to zero for a mature project.

This is not abstract. It surfaced concretely in Skills Manager: roughly **16 local memory files** had quietly become a parallel, invisible knowledge base, overlapping what already lived in GitHub and Notion. That is exactly the anti-pattern this model exists to prevent. The full cautionary tale is in [knowledge-homes.md](knowledge-homes.md).

## The decisive rule

> **A substrate is allowed to hold knowledge only if it is versioned + visible + cold-resumable.**

Git is. Notion is. A chat transcript and a local memory file are not. Every placement decision below is just this rule applied. When you are unsure where something belongs, you are really asking which substrate can carry it — and the answer is never the transcript.

## The model: two axes, four homes

Knowledge sorts on two axes:

- **Scope** — is this about *this project*, or about *how we operate* across every project?
- **Kind** — is this *transient work* (what to do, what's decided) or *durable knowledge* (architecture, conventions, hazards, strategic "where we are")?

Two axes give four quadrants, and each quadrant has exactly one home. **Nothing lives in two homes.**

| | **Project-scoped** | **Global / business** |
|---|---|---|
| **Work** (what to do, what's decided) | GitHub issues + PRs | Notion Briefs DB (progress, time-series) |
| **Durable knowledge** (architecture, conventions, hazards, strategic state) | Repo docs (technical canon, git-versioned) + Notion Project Overview (strategic, human-facing) | Skills + global `CLAUDE.md` |

The four homes in depth — including the two-flavors-of-source-of-truth refinement and the minimal repo contract — are in [knowledge-homes.md](knowledge-homes.md).

## How a project gets here

A project is not born externalized. It moves through three phases — inception (live, in chat), the externalization event (the deliberate dump to durable substrate), and the graveyard phase (self-describing, externally-driven). The externalization event is the whole game. See [lifecycle.md](lifecycle.md).

## The executable canon (skills)

These docs say *why*; the skills say *how*. The load-bearing procedures:

- **`graveyard-shift`** ([skills/graveyard-shift](../skills/graveyard-shift)) — drain the backlog autonomously off durable state; the core working loop this model serves.
- **`setup-graveyard-project`** — the ceremony that performs the externalization event (lifecycle step 2): backlog → issues, canon → repo docs, strategic state → Notion Overview.
- **`observation-mode`** — ship into a watched observation phase instead of treating merge as the end; the eval substrate for judgment-shaped work. The signal that proves it's behaving must be **instrumented into the shipping PR and queryable** — the read/observability slice ships *with* the change, so a later sweep adjudicates by running a query, not by guessing.
- **`shape-an-epic`** ([skills/shape-an-epic](../skills/shape-an-epic)) — turn an underspecified issue into a concrete proposal with recommendation, sketch, and trigger criteria.
- **`pr-package`** ([skills/pr-package](../skills/pr-package)) — open a PR as a decision package with the load-bearing calls surfaced for review.
- **`notion-briefs`** ([skills/notion-briefs](../skills/notion-briefs)) — set up and publish to the shared cross-project Notion Briefs DB.
- **`credit-pacing`** — check budget before spending it and pace work around overage instead of grinding into it.

## The other two docs

- [lifecycle.md](lifecycle.md) — the three-phase lifecycle and why the externalization event is the whole game.
- [knowledge-homes.md](knowledge-homes.md) — the four homes in depth, the two flavors of project source-of-truth, the minimal graveyard-ready repo contract, and the local-memory anti-pattern.
