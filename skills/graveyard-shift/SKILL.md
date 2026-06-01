---
description: Work through the open issue backlog autonomously. Auto-ship the small clean fixes, prep draft PRs for review on bigger ones, file refined proposals when design choices need user input. For unattended sessions where the user is sleeping / away and wants to wake up to a productive set of changes.
---

# Graveyard Shift

The user is away (asleep, in a meeting, on a flight) and wants you to drain the issue list while they're gone. You triage each open issue into one of four buckets, execute the cheap ones end-to-end, prep prototypes for the design-laden ones, file proposals for the wholly-undecided ones, and surface a clean inventory when they return.

The user reviews the queued material when they're back. The skill's job is to maximize what they wake up to — not to make every call themselves.

## The contract: decisions, never confirmations

This is the load-bearing principle. The user's morning attention is for **decisions** — judgment calls only they can make. It is NOT for confirmations — "is this fix right?", "should I merge?", "does this look ok?". Those are answerable by other AIs (codex review, type-checkers, the build) without spending the most expensive resource.

**Codex IS the second opinion.** Run `codex review --base main` on every PR before merging. No findings or only nits → ship. Substantive findings → patch them, also without asking. The user does not need to re-validate work codex already validated.

**Default to shipping.** If codex passes, type/cargo check passes, the diff is on-policy: merge. Do not queue "want me to merge?" Do not pre-announce intentions like "I'll patch #X then check #Y then ..." — those are confirmation-seeking dressed as status updates. Just do the work and report what landed.

**Mechanical work is not a decision.** Both branches added a field → keep both. Single-region textual conflict where intent is obvious → resolve and continue. These are not "want me to ...?" questions.

**Structural surgery IS a decision.** When one branch refactored what the other extended (e.g., a 4-region 130-line conflict where one PR split a class and the other added methods to the old shape), your guess at intent could be wrong. Surface it.

**The boundary, sharpened:**

| Looks like ... | Bucket |
|---|---|
| "Codex flagged a P2; here's a 5-line fix; want me to apply it?" | **Just apply it.** This is a confirmation. |
| "Single-file rename, all references updated, tsc clean, codex clean." | **Just merge.** |
| "Both PRs touch settings.rs — both add a new field — keep both." | **Just resolve and merge.** |
| "PR #A refactored what PR #B extended; merging requires deciding whether B's registry lives on A's new class or stays on the old one." | **Surface as decision.** Intent matters. |
| "Issue is one sentence, no problem statement, can't sharpen from context." | **Surface as decision.** No basis to act. |
| "Branch is a known-broken implementation per issue #N; should it close or be reworked?" | **Surface as decision.** Scope call. |

If you find yourself drafting a message that ends in a question mark and the answer would just be "yes, do that" — delete the draft and do it.

## The four buckets

### 1. Auto-ship — small, codex-flagged, clean

Ship directly with full codex-pr loop:

- Codex-flagged bug fixes with a concrete fix sketch in the issue
- Defensive additions following an established pattern (e.g. gate skills like routes were gated)
- Wrong-payload fixes, missing-await fixes, idempotency tightening
- Single-file changes with obvious correctness

**Test:** could you describe the change in one sentence? Would a senior eng look at the diff and immediately agree? Does the issue itself say "fix sketch: …"? If yes to all, auto-ship.

For each:
1. Spin a worktree off `origin/main` (named for the topic, see worktree rules)
2. Implement the fix
3. Tests + tsc clean
4. Open PR, run codex review loop (judgment gate, stopping rules)
5. Merge when clean (or stopping window hit with only manageable P2s — apply silently per skill exception and ship)

### 2. Prep — concrete code, but wants the user's eye

Build the prototype, push as a **draft PR**, leave open for review. Do NOT merge.

- New tools / features where the implementation has obvious knobs to pick
- UI changes where the visual or copy choice matters
- Behavior changes with multiple reasonable shapes
- The issue spells out direction but the user hasn't said "ship it"

For each:
1. Worktree → branch
2. Build the most-defensible default in code
3. **PR description carries a "Things to push back on" section** listing the knobs you picked and alternates — gives the user concrete things to swap rather than asking abstract questions
4. `gh pr create --draft` — do not merge

### 3. Proposal — design-laden, premature to code

**Default to `shape-an-epic` for anything epic-shaped.** Post a structured proposal comment on the issue, skip the worktree.

This bucket is bigger and more aggressive than first instinct suggests. **An 80%-good-enough proposal you can iterate on beats a vague issue that sits.** The user has a bias toward motion: shape the thing, surface it, let the next review pass refine. Don't wait for perfect alignment to surface a direction — surface the direction, let alignment happen on the proposal itself.

Use `shape-an-epic` (the heavyweight 8-section format — status check → recommendation → sketch → what's-not-changing → sequencing → rabbit holes → out-of-scope → trigger → related) for:
- Multi-phase migrations
- Architectural calls with several reasonable paths
- Year-old issues whose problem statement may have decayed
- Strategic-thread issues that need a milestone marker / replan
- Anything where "the work to write the proposal" is itself ≥ 10 minutes of careful thinking

Use the **lightweight 4-bullet format** below ONLY when the issue is a small note that genuinely doesn't deserve 20 minutes — a yes/no design question, a simple copy choice, a one-knob tradeoff:

- **What you'd recommend and why** (concrete, not "here are options")
- **What you'd build** (sketch — schema, tool shape, file list)
- **Estimated PR size**
- **"Want me to build it?"** as the closing call to action

When in doubt between lightweight and `shape-an-epic`: pick `shape-an-epic`. The cost of over-shaping is 15 extra minutes of writing; the cost of under-shaping is the issue rotting until next month.

### 4. Skip — true blockers only

The skip bucket is the smallest one. Be aggressive about ruling things INTO another bucket; reserve skip for two narrow cases:

**4a. Hard-dependency blocked.** Issue requires something that demonstrably hasn't shipped — not "would need design first" (that's a `shape-an-epic` proposal), but "literally cannot be built until X lands." Examples: needs a new database column the migration hasn't run; needs an endpoint that doesn't exist yet; needs a third-party API access that's pending.

**4b. Unformed idea, needs Ray's input to make any progress.** The issue is a single sentence with no problem statement, no surface area named, no shape to react to. *And* you can't sharpen it from codebase context alone (would just be guessing what the user meant). These should still be cheap to identify — typically the user themselves filed them as "remind me to think about X."

Everything else routes to one of the action buckets:
- Parent meta-issues / umbrella threads → `shape-an-epic` with the "audit + replan" flavor (annotate what's shipped under it, scope what's left)
- Observation tasks (user has to look at logs) → still useful to file a proposal naming WHAT the operator should look for and WHEN; that's not skip, it's a sharpened observation issue
- Speculative bug fixes for unobserved shapes → `shape-an-epic` with explicit "When to pick up" naming the observable signal
- Issues blocked on a parent that requires user approval → check if you can land the parent's *unblocked* child first; if not, `shape-an-epic` the parent so the approval gate is concrete

Skip should fit in a short list at the end of the summary. If skip is more than ~25% of the backlog, you're skipping things that wanted shaping.

## Execution order

Proposals are not the slow tail. They ship as eagerly as auto-ships — they're cheap (one comment per issue, no codex loop) and they compound for the user's morning review:

1. Auto-ship pass: knock out each cleanly. The user wakes up to N green merges.
2. Prep pass: 3-5 draft PRs is a productive morning of review. More than that and the user can't get through them over coffee.
3. **Proposal pass: shape every epic-shaped issue you can.** Use `shape-an-epic` aggressively. Each proposal is 15–25 minutes of focused thinking; ten of them in a night is a transformed backlog. The user has a bias toward motion — 80%-good-enough proposals are the artifact that lets the next pass be a refinement, not a from-scratch.
4. Skip pass: note in the final summary, no action.

Proposals are LOWER overhead than auto-ships (no PR, no codex loop, no merge) and HIGHER leverage on backlog clarity. Don't sandbag this pass.

## Triage gotchas

- **Stale diagnoses.** Old issues may describe problems already partially fixed by intervening PRs. Read the issue, then verify against current code before believing the diagnosis. Surface stale findings as a refined-proposal comment.
- **Dependencies.** If issue A is blocked on issue B (B needs user approval), do B's child issues first if they unblock the bigger arc. Don't paint yourself into corners requiring approvals you don't have.
- **Codex round budget.** Auto-ship items can chew 4-6 codex rounds. Don't keep pushing a single PR past round 8 — that's the architecture telling you the diff is wrong. Stop, file follow-ups, surface to user.
- **Worktree node_modules.** Worktrees off `origin/main` need their own `node_modules` (or a symlink to a recently-installed one in another worktree). The first worktree of the night usually pays the install cost; later ones can symlink.

## What "ready" looks like at the end

**Two artifacts, both mandatory:**

### 1. A fresh dated brief

Write `test-plans/graveyard-brief-YYYY-MM-DD.md` (or the equivalent docs path for the project) reflecting **current** state. Coming in to a brief dated yesterday that doesn't match today's repo is worse than no brief — it actively misleads.

**Rules for the brief:**
- One per shift, dated. Supersede or delete prior briefs in the same doc — don't accumulate stale ones.
- Open with a TL;DR of what landed and what's blocked.
- **The decision section is the spine — but the spine is short.** Most shifts surface **0–3** genuine decisions. If your decision section has grown into a categorized list of ten-plus items ("B1 agent stuff, B2 search stuff, B3 features…"), STOP: you have collected a backlog and dressed it as decisions. Go back and resolve. A brief that hands the user a backlog has failed its core job.
- **The two-part decision test.** A line item earns a place in the decision section ONLY if BOTH are true: (1) the answer genuinely *forks the work* — different answers send you down materially different paths; AND (2) you *cannot derive the answer yourself* from the codebase, the North Star, or "take the biggest swing." If either fails, it is not a decision — handle it per the table below.

| It's really… | What you do (NOT surface as a decision) |
|---|---|
| "Which of these N issues should I do next?" | **Pick one and run.** Sequencing is yours. The user does not adjudicate your work queue. |
| "Do we want feature X?" with no shape | Either it's on-North-Star → build the most-defensible version; or it's genuinely speculative → `shape-an-epic` it into a concrete A/B/C proposal *on the issue*, not a bare "want this?" in the brief. |
| "Here are my own open/draft PRs" | **Not a brief item at all.** The user's own PRs are not something you surface back to them. Delete. |
| "Should I merge this clean, codex-passed, self-authored fix?" | **Merge it.** (Per "decisions, never confirmations" above.) |
| A cluster of related issues sharing a root cause | Propose ONE campaign with a recommended sequence and *just start it* — don't enumerate the children as separate decisions. |

- **A real decision reads as a fork, not a menu.** Good: "PR #A refactored what #B extended — B's registry can live on A's new class (cleaner, +2hr) or stay on the old shape (faster, leaves debt). I recommend the former. Confirm?" Bad: "Here are 12 open features grouped by theme, which do you want?"
- Status of completed work is a one-liner table at most. The user doesn't need a play-by-play.
- "What I'm doing without you" is a first-class section, not an afterthought. List the calls you took back (sequencing, shaping, clean merges) so the user sees you're *running*, not stalled. The brief's two jobs are: **(1) catch the user up, (2) extract the few genuine forks.** Everything between those two is work you should already be doing.
- "Items NOT requiring a decision" / cleanup (locked worktrees, stale files) goes at the bottom and stays small. If it's truly trivial, just do it instead of mentioning.

### 2. The terminal summary

A short message in the conversation that fits on one screen:

```
### Shipped (N merged PRs)
| PR | Issue | Title |
| ... |

### Queued for review (M draft PRs)
| PR | Issue | Title | What you decide |
| ... |

### Surfaced as proposals (K issue comments)
- #N — one-line direction taken

### Decisions waiting on you (see brief)
- short pointer per item, not the full decision body
```

Each draft PR's description should already carry the "Things to push back on" section so the user can walk through them with coffee without re-asking what the choices were. The terminal summary points at the brief for full context — don't repeat the brief in chat.

## Auto-ship vs prep — the borderline call

These often look similar. The dividing question: **could the user reasonably want a different shape than the one you'd pick?**

- Fix a wrong payload format the spec defines → auto-ship (no shape choice)
- Add a defensive gate following a pattern that already exists → auto-ship (pattern is set)
- Add a new admin tool with multiple reasonable signatures → prep (signature is a choice)
- Change copy / wording → prep (taste belongs to the user)
- Rewire a hot read path → prep, sometimes proposal (design implications)

When in doubt, prep. The cost of preparing a draft PR for review is low. The cost of merging the wrong shape is a force-pushed branch + lost trust.

## When NOT to use this skill

- The user is awake and engaged — work synchronously instead, talk through trade-offs in real time.
- There's one specific issue to work — just work it; don't sweep the backlog.
- The backlog is mostly architectural decisions — those want a synchronous session, not a graveyard sweep.
- You don't have full triage context yet — read enough issues to understand the landscape before committing to a sweep plan.
