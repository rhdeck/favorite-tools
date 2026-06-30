---
name: observation-mode
description: Ship work into a watched observation phase instead of treating merge as the end. When you close an issue, reopen it for observation with a named signal to watch; graduate it to closed-stable only after a quiet window; catch regressions as regressions. The eval substrate for judgment-shaped work that can't be red/green-tested — and the mechanism that lets you ship MORE, because shipping sets up observation rather than ending the story.
---

# Observation Mode

**Shipping is the beginning, not the end.** Most of what we build here is *judgment-shaped*, not *contract-shaped*: it's a feature, a way of framing a problem, a default we picked — not an if-this-then-that invariant. That kind of work can't be validated by a red/green test (TDD presumes a fixed contract to assert against). It can only be **watched**. Observation mode is the eval substrate for it: ship the thing, name what would tell us it's misbehaving, watch for that signal over a window, then either graduate it to stable or catch the regression.

Strict TDD still applies where it fits — a real if-this-then-that invariant (a payload format, an idempotency guarantee, a parser edge case) deserves a test, and a test that would catch a class of breakage is cheap insurance. Don't skip a genuinely testable contract. But **don't force feature/judgment work into a test shape it doesn't have** — that produces brittle tests that assert an arbitrary current shape and break the moment we improve it, bringing the system down for no signal. For that work, observe.

The whole point: **this gives you permission to ship more.** A change that today would sit as a draft PR "because I have a little concern" can instead ship-into-observation — the concern becomes legible *with data*, which you only get by shipping and watching. The safety net moves from *pre-merge human review* (expensive: the user's attention) to *post-merge watched signal* (cheap: a label + a dated note). Shipping is less of a commitment when it's set up for observation, so the bar to ship drops.

## The lifecycle (single-issue identity)

One issue carries the work through its whole life. The phases are GitHub state, so the register is just `gh issue list --label observing` — no new infrastructure.

1. **Build.** Implement → review → PR merges with `Closes #N`. The build phase is genuinely complete, so the issue closes. Good — that close is real.
2. **Observe.** *Immediately reopen #N*, add the `observing` label, and post the **observation contract** (below). The reopen is the ceremony: the GitHub timeline reads "closed → reopened," which visibly marks the phase change from *built* to *being watched*. The issue now lives in the observation register.
3. **Graduate.** At a later sweep, past the review-by date with no signal fired: close #N for real and label it `regression-candidate`. It has earned a regression test *now* — you'd be guarding proven-stable behavior, not speculating. (Writing the guard is optional follow-up work, not a blocker to graduating.)
4. **Regress.** If a signal fires — often surfaced as a *new* issue that turns out to be the watched behavior breaking — don't file a fresh bug in isolation. **Reopen the observation issue** (or keep it open), link the triggering report, and note the regression. The contract already told you what to look at, so diagnosis starts ahead.

## Setup: ensure the labels exist (any repo, idempotent)

This skill is cross-project. The first time you use it in a repo — and harmlessly every time after — ensure the two labels exist. `gh label create` is idempotent-safe when you ignore the "already exists" error, so just run:

```bash
gh label create observing --color "0e8a16" \
  --description "Shipped and under active observation — watching a named signal before final close" 2>/dev/null || true
gh label create regression-candidate --color "5319e7" \
  --description "Graduated from observation with no adverse signal — stable enough to seed a regression guard" 2>/dev/null || true
```

Do this as a reflex in any project that adopts observation mode — including from inside a `graveyard-shift` (a worker that ships-into-observation should ensure the labels first). The register (`gh issue list --label observing`) only works if the labels are present, so a project that runs into this consideration should set them up the moment it does, not later. No central registry is needed — the labels live per-repo and this snippet brings any repo into compliance on first contact.

## The observation contract

When you ship into observation, the reopened issue gets a comment with exactly these beats. Keep it tight — this is the thing a future sweep (or a future you) reads to decide graduate-vs-regressed.

- **Shipped:** PR #N, date. One sentence on what changed / what now exists that didn't.
- **Watch for:** the *single most likely way this misbehaves* — stated as an observable, not a worry. "Sync silently no-ops on a symlinked dest" not "sync might be flaky."
- **Signal source (required):** the concrete artifact a future sweep *reads* to adjudicate this — not prose about symptoms. Three parts, all required:
  1. **Artifact** — the production thing that records the signal: a specific log line/event, a counter/metric, an error class, a dashboard/DB query, or a named non-code channel (a user-report inbox, a follow-up-issue check). For instrumentable changes, **this artifact must exist** — if the "watch for" needs a log line or counter that production doesn't emit yet, *building it is part of this PR* (see eligibility gate #2).
  2. **How to read it** — the literal command a future shift runs: the `grep`, the SQL, the dashboard URL, the `gh issue list` filter. Copy-pasteable, not "check the logs."
  3. **Threshold** — what reading is healthy vs. regressed: "0 occurrences," "error rate < 1%," "no user reports in the window." This is what the sweep compares its reading against.

  *Worked example:* Artifact — `log.warn("event=sync_skip reason=symlink dest=…")` emitted by the new guard (added in this PR). How to read — `grep 'event=sync_skip' /var/log/app/*.log | wc -l`. Threshold — `0` (any occurrence means the symlink path is being hit and the guard's assumption is wrong → regression).
- **Review by:** a date. Default window **14 days**; shorten for low-risk/high-traffic changes (a week), lengthen for rarely-exercised paths (a month). Past this date with a healthy reading → graduate.
- **Revert:** one line on how to back it out if the signal fires (usually "revert PR #N"). Confirms reversibility was real.

A contract you can't fill in — specifically, a **Signal source** you can't make concrete and queryable — is the signal that this should NOT have shipped into observation. Route it back to a draft PR or proposal.

## Eligibility: what may ship-into-observation

Three gates, **all required**. This is the discipline that makes the looser ship-bar safe:

1. **Reversible.** A cheap, clean revert exists (revert the PR, flip a flag). If backing it out is expensive or messy, it's not observation-eligible.
2. **Instrumented signal.** You can name the observable misbehavior, the **production artifact** that records it, the **query** to read that artifact, and the **threshold** that separates healthy from regressed — *and that artifact actually exists, or is added in this PR.* Naming the misbehavior is no longer enough: *nameable ≠ queryable.* If "watch for X" needs a log line, counter, or metric production doesn't emit, **building it is part of the diff** — same PR, same review. A signal you can describe but cannot query — because the instrumentation the PR would need isn't there — is **not** observation-eligible: it falls back to a **draft PR (prep)** or **proposal**, exactly as a failed gate does. ("How would the next shift know this regressed?" must be answerable *from the diff*, not reconstructed at sweep time.)
   - **Carve-out — non-instrumentable work observes differently.** Some changes have no production signal to query: planning/eval issues, strategy threads, copy/taste calls, doc edits. For these the Signal source is legitimately a concrete **non-code channel** — "the user reports the framing still confuses them," "no follow-up issue filed within 14d" — still a named artifact + a way to check it + a threshold, just not a log line. The gate forces *concreteness of where-to-look*, **not a code metric in every case.** It applies to changes that *can* be instrumented; it does not invent metrics where there is nothing mechanical to measure. The carve-out is **not** a loophole for instrumentable code: if a code change has a real misbehavior to watch, it is observation-eligible **only** with a queryable Signal source — you cannot downgrade it to a prose channel to dodge the instrumentation.

   **The trivial-fix case is the opposite of a loose signal — it doesn't enter observation at all.** A one-line copy fix or obvious defensive gate whose revert is free has no misbehavior worth watching: just **auto-ship and merge it, with no observation contract.** "No metric" here means "no observation," not "observe with a vague signal." Instrumentation scales with *risk*: a change risky enough to watch needs a queryable source; a change trivial enough to skip the watch skips it entirely. And when you *do* instrument, a `grep`-able log line is almost always enough — don't stand up a metrics framework where a log line suffices.
3. **Internal blast radius.** Failure is contained: no data loss, no irreversible external side effect, nothing published outward (no public-repo push, no third-party send, no destructive migration). Outward-facing or destructive changes still need pre-merge human sign-off regardless of how watchable they are.

Pass all three → **ship and watch.** Fail any → it stays a **draft PR (prep)** or a **proposal**, per the normal buckets. Observation mode widens the auto-ship lane; it does not abolish the prep lane.

## Triage: cross-reference incoming work against the register

Observation mode changes how you read *new* issues, not just how you close old ones. **Before triaging an incoming bug as novel, check it against `gh issue list --label observing`.** Ask: *is this a watched signal firing?* If a new report matches the "watch for / signal source" of something under observation, it's a **regression**, not a fresh bug — fold it into the observation issue (reopen/link, phase 4) instead of opening a parallel thread. This is the payoff of having named the signal up front: regressions get recognized as regressions, with a head start on diagnosis, instead of being misfiled and re-investigated from scratch.

## Use outside graveyard too

This is a general close-protocol, not a graveyard-only ritual. Any time you (or the user) ship judgment-shaped work — in a live session, a one-off PR, anywhere — prefer **close → reopen-for-observation** over a bare close when the three gates pass. The register is cross-cutting; graveyard is just its busiest writer and reader.

## How graveyard shift uses this

The `graveyard-shift` skill references observation mode at three points — see that skill for the integration, summarized here:

- **Start of shift — observation register sweep.** Right after the stale-draft sweep, pull `gh issue list --label observing`. For each, **run its Signal source query and record the reading as a dated note on the issue** — adjudication is "ran `<query>`, got `<reading>`, vs threshold `<X>`," not a vibe check. Reading at/under threshold past the review-by → **graduate** (close, `regression-candidate`); reading over threshold → **regression**, route into the wave as a fix with its diagnosis already started; still cooking → leave it, and record its **age + last reading** in the brief ("#N observing 9 days, watching for X, last reading: 0 hits as of 6/30").
- **Auto-ship / prep boundary.** Items that would have been draft-PR preps but pass the three eligibility gates **ship-into-observation** instead — merge, then reopen with the contract. This is the loosened ceiling. It does *not* raise the draft-PR cap; it *moves items out of* that cap into shipped-and-watched.
- **Brief — observation register section.** The shift report carries a register block: what graduated, what regressed, and what's still observing with ages. An item observing well past its window is itself a thing to surface ("#N has been observing 40 days — graduate or it's just open").

## Anti-patterns

- **Observation as a dumping ground.** The register is not where uncertain work goes to be forgotten. Every `observing` issue has a review-by date and gets adjudicated at the next sweep. An issue observing far past its window is a failure, not a holding pattern — graduate it or act on the signal.
- **Skipping the contract.** Reopening with just the `observing` label and no "watch for / signal source / review-by" is theater — there's nothing to observe. The contract is the substance; the label is the index.
- **Naming a signal with no production source.** A "watch for X" with nowhere to read X is the new face of skipping the contract: the contract *looks* filled in but cannot be evaluated. If the instrumentation that would make X queryable isn't in the diff, you haven't shipped an observation — you've shipped a worry. Build the source or route to prep.
- **Forcing a test where observation fits.** Don't write a brittle assertion against an arbitrary current shape just to have a green check. If the thing is judgment-shaped, watch it; reserve tests for real invariants.
- **Re-filing a regression as a novel bug.** If it matches a watched signal, it belongs on the observation issue. A parallel bug thread loses the head start the contract gave you.
- **Graduating on a timer alone when the path is barely exercised.** "14 quiet days" only means something if the code actually ran. If a watched path hasn't been hit (low traffic, seasonal feature), note that and extend the window rather than graduating on silence that proves nothing.
