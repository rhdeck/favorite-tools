# Inter-project Coordination: issues as the message bus

How one autonomous project affects another. This is the operational detail behind one cell of the four-homes grid in [operating-model.md](operating-model.md) — *Project work → GitHub issues* — extended into its cross-project meaning: **GitHub issues are not only a project's own backlog, they are the message bus between projects.** The concept lives here; the skills that enact it point back to this doc.

## Each project is an autonomous division

Every repo is its own **vice president of a division, handling its own territory.** A project's graveyard shift governs its own work: it triages its own backlog, adjudicates its own decisions, and owns what lands in its tree. The division has an orchestrator, a source of truth (its issues + docs + Overview), and the authority to decide how its own work gets done.

The load-bearing consequence is a boundary: **outsiders do not reach into a division's repo and do the work themselves.** Not another project that needs something from it, not a human in a planning conversation, not an automated loop firing on a schedule. Doing the work *for* a division bypasses its orchestrator — the one actor that holds the division's full context and can weigh the request against everything else in flight. A change injected from outside, executed directly, is exactly the kind of unversioned-by-that-repo, unadjudicated, context-free edit the whole model exists to prevent.

## Discovery: how you find the divisions you can talk to

Before you can message a division you have to know it exists and where it lives. There is **no hardcoded roster** — the registry is two Notion databases, read live, and both are already substrates this model maintains:

- **The Project Overviews DB is the org chart.** One page per project — the directory of every division. Each page carries the project's name, one-line purpose, status, and, load-bearing, its **Repo** field. That Repo field *is the division's address*: it is where you inject to reach it. Enumerate the roster with `python3 ~/.config/ai-briefs/notion_briefs.py overview list`.
- **The Briefs DB is the status wire.** The newest-first time-series of what each project has been doing (briefs, shift reports). Read a division's recent briefs to understand its current state and confirm it's active *before* you message it — you address the division as it actually is, not as you remember it.

So the sequence to send information to another project is always:

1. **Find it** — look it up in the Project Overviews (name + repo), and skim its recent Briefs for context.
2. **Address it** — take the target repo from that Overview's Repo field.
3. **Message it** — inject a GitHub issue into that repo (next section).

This is why a blank Repo field is not a cosmetic gap but a routing failure: **a division with no address in the Overview cannot be reached** — you have no repo to inject into. (This is exactly what the sc-auth orphan exposed; see the atomicity rule in [DECISIONS.md](DECISIONS.md).) The Overviews DB is the company org chart, the Briefs DB is the status wire, and — per the next section — GitHub issues are the inter-office mail.

## The only sanctioned cross-project action: inject an issue

> **When one app wants to affect another, the way it does it is by injecting an issue into the target's repo — and that causes the other app and its orchestrator to consider that issue and make decisions about how to bring it to bear.**

The GitHub issue is the **async message** — the RPC — between autonomous agents. The requester does not execute; it *enqueues intent* in the target's own system of record. The target's orchestrator adjudicates on its next shift: it considers the issue, decides **how** — or **whether** — to act, and brings it to bear on its own terms, sequenced against its own backlog. Request and execution are decoupled; the requester never holds the target's context and never needs to.

This is why the message bus is an issue and not a call:

- **It is durable.** The request survives the moment it was made; it does not evaporate when the requesting process ends.
- **It is versioned + visible + cold-resumable** — the same rule that governs every substrate in this model ([operating-model.md](operating-model.md), "The decisive rule"). An issue in the target repo has history, is watched, and can be picked up cold by whatever shift drains the backlog next. A synchronous trigger has none of these properties.
- **It respects the division boundary.** The target's orchestrator stays the sole author of changes to its tree. The requester supplies a *want*; the division decides the *how*.

This *extends* the four-homes rule. "GitHub issues = project work" already made issues the backlog and decision record for a single project ([knowledge-homes.md](knowledge-homes.md), "Project work → GitHub issues + PRs"). The same substrate, read across repos, is the **inter-project message bus**: an issue in your repo may be *your* backlog item or *another division's request to you*, and both are handled the same way — the orchestrator triages and adjudicates on its next shift.

## Loops become async issue-injection, not synchronous triggers

This is also the model's stance on the "agent loops" others reach for — a loop that immediately triggers an agent to *do X now*.

> **This becomes our approach to loops. Instead of loops that immediately trigger an agent to do X, we have loops that inject issues right into the GitHub repositories for those projects — and as their graveyard shifts come up, they just run those.**

A recurring coordination need — "every night, re-check Y across these projects," "when metric Z trips, get project P to react" — is expressed not as a live trigger that drives a target agent synchronously, but as a loop that **injects durable issues** into the target repos. Execution happens **asynchronously**, when each target's own shift drains its backlog. The loop's job ends at *enqueue*; the division's shift picks it up on its own clock.

Why this is the right shape, and not just a stylistic preference:

- **It decouples requester from executor.** The loop does not block on, drive, or hold context for the target. It drops a message and moves on.
- **It turns coordination into state instead of a trigger.** A live in-memory trigger is invisible, unversioned, and gone the instant it fires. An injected issue is a versioned, visible, cold-resumable artifact — coordination you can *see in the backlog* and resume after a crash, exactly like every other unit of work in this model.
- **It is what lets the whole system scale asynchronously.** Divisions run on their own shifts, at their own cadence, without a central conductor holding every project's context at once. The bus absorbs the coordination; no synchronous fan-out has to stay resident. This is the async idea-business the north-star vision points at (see [`docs/VISION.md`](VISION.md)): manifestations in software, content, and services, coordinated through durable messages rather than a live central loop.

## The worked example: the Project Overviews rollout

This protocol already has a first instance. The Project Overviews rollout needed ~10 projects to each fill in their own Overview page. It did **not** fill them centrally. It **injected a fill-issue into each repo** — one `graveyard-infra` issue per project — so that **each division fills its own Overview on its own shift**, adjudicated by its own orchestrator.

That is this protocol in action: coordination across ~10 autonomous divisions carried entirely by injected issues, with each division doing its own work when its shift comes up — never a central actor reaching into ten repos. The atomicity rule that page-creation and fill-issue-injection are one indivisible step (an unfilled page with no driving issue is an orphan bug) is recorded in [DECISIONS.md](DECISIONS.md) (2026-07-01), and the mechanics live in the [`setup-graveyard-project`](../skills/setup-graveyard-project/SKILL.md) skill and the `graveyard-infra` fill-issues it emits.
