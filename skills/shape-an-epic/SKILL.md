---
name: shape-an-epic
description: Turn an underspecified open issue (an "epic" — design-laden, multi-phase, no clear path) into a concrete proposal comment with a recommendation, sketch, phase plan, and trigger criteria. Use when the user says "shape this", "turn #N into a proposal", or when an issue is too big to auto-ship and too design-heavy to prototype without input. Builds on Basecamp's Shape Up pitch format (Problem, Appetite, Solution, Rabbit Holes, No-gos), adapted for GitHub-issue-as-proposal artifacts.
---

# Shape an Epic

You're being asked to take a vague, design-heavy issue and sharpen it into a concrete proposal — concrete enough that a future implementer (you or someone else) can pick it up without re-deriving the design, rough enough that they still get to make implementation calls.

The output is a **comment on the existing issue**. Not a new issue. Not a PRD. Not code. A proposal that lives where the decision needs to be made.

## When this skill applies

Use this when an issue:
- Has multiple plausible directions, no obviously-right one
- Is too big for a single PR
- Has a stub-shaped body ("we should migrate X off Y") with no design
- Was filed before context that may have moved the problem (recent merges, shipped patterns)
- The user explicitly asks to "shape #N" or "turn this into a proposal"

Don't use this when:
- The issue is small enough to auto-ship — just ship it
- The issue already has a complete PRD or implementation sketch
- The user wants to start *building* (use a different flow — write-a-prd, prd-to-issues, or just spin a worktree)
- The diagnosis itself is suspect — verify by reading code first; if it's wrong, file that observation as a status check, don't dress it up as a proposal

## Process

### 1. Read the issue with current eyes

- `gh issue view <N> --json title,body,comments,labels`
- Note the file date / referenced PRs. **Issues decay** — what was true at filing may have been partially fixed by intervening work. Surface staleness; don't propose against a snapshot that no longer matches reality.
- **Always sanity-check the issue's claims against the codebase, even if the issue is fresh.** Issue bodies routinely assert "X has shipped" or "Y is in place" — those claims rot or are written aspirationally. A 2-day-old issue can have a wrong claim about state. Verify before believing.

### 2. Survey current state in the codebase

Spot-check the files, patterns, and adjacent issues the proposal will touch. You're looking for:
- **Already-shipped pieces** that resolved part of the issue (write them as "Status check" up top)
- **Established patterns** the proposal can reuse (cite by file path — "mirror `mental_models` + `mental_model_drafts`")
- **Adjacent issues** that should ship in lockstep or block this one

Budget for this step: 5–10 grep/read calls. If you need 30, the issue isn't really an epic — it's a research project. Surface that instead of forcing a proposal.

### 3. Identify the decision tree

What architectural calls does this issue actually require? List them out before writing anything. Typical shapes:
- Where does the data live? (filesystem / Postgres / Spaces / external)
- What's the read path? (sync / cached / canonical / fallback chain)
- What's the write surface? (admin tool / migration / API endpoint)
- How does it sequence? (one PR / phased / blocked on another epic)
- What's *not* changing? (existing surface area to preserve)

For each call, pick the answer you'd defend in code review. **State it. Don't list options.**

### 4. Draft the proposal — the seven sections

Use this skeleton. Each section earns its keep or gets cut. Adapt language to the issue's domain — these are scaffolding, not chapter titles you must use verbatim.

```markdown
## Proposal — [one-line headline of the direction]

### Status check
[What you verified against the current codebase. What's already shipped
that the original issue assumed wasn't done (or claims is done that
isn't). What's moved. What's still open and unblocked. Always include
this — even on fresh issues — because the act of writing it forces the
sanity-check. If nothing has shifted, one line is fine: "Verified against
main as of <SHA>: state matches the issue's framing."]

### Recommendation
[The direction, stated as a recommendation, not a menu. One paragraph. The
reader should be able to stop here and understand the call.]

### What you'd build (the sketch)
[Concrete enough to evaluate. Schema in code blocks. File paths. Tool
shape. UI layout. The level of detail where a senior eng can say "yes
that would work" or "no, here's the problem" — not so detailed that
implementation choices are pre-decided.]

### What's NOT changing (surface area preserved)
[Existing behavior, wiring, or contracts the proposal explicitly keeps.
Skip when truly nothing is load-bearing, but most non-trivial proposals
have something here. Naming it up front prevents an implementer from
"helpfully" refactoring adjacent code that the design depends on.
Examples: "the existing 1.5s conversation poll stays wired; the new
phase just changes what it surfaces", "registerAppTool's existing
signature is not changing — new behavior is opt-in via a new arg".]

### Sequencing
[Phases as separate PRs. Each phase: title, what it changes, what's
independently shippable. Roughly Shape Up "appetite" per phase — half a
day / one day / two days / a week. Be honest; a "small PR" that's three
days of work derails the whole exercise.]

### Rabbit holes
[Implementation details worth surfacing now so the implementer doesn't
fall in. Race conditions you've spotted. Migration order. State machines.
Things that look easy and aren't.]

### Out of scope
[Explicit punts. "Multi-X anchors" / "per-user preferences" / "history
table." Each line earns its keep: a punt that's never going to be asked
for is dead weight; a punt that will be asked for *immediately* probably
isn't really out of scope.]

### When to pick up
[The trigger. Specific. "When N users hit X" / "when telemetry shows Y" /
"when feature Z lands" / "shippable now, phase 1 is half a day." Avoid
"when needed" — name the signal.]

### Related
[Links to issues this depends on, blocks, or shares pattern with.
[[name]]-style memory-style cross-references are fine if relevant.]
```

### 5. Post the proposal

`gh issue comment <N> --body "$(cat <<'EOF' ... EOF)"`

HEREDOC for multi-paragraph bodies. Don't open PRs, don't spin worktrees — the artifact is the comment.

### 6. Update task tracker / report back

If invoked from graveyard-shift, log it as a "Surfaced as proposal" line. If invoked standalone, summarize what you posted and link the comment URL.

## Anti-patterns

These are the failure modes that turn a proposal into noise:

- **Listing options without a recommendation.** "We could do A, B, or C" forces the user to make the design call you were supposed to make. Pick A, explain why, mention B/C only when the tradeoff is real and the reader genuinely needs to weigh in.
- **Implementation depth without a sketch.** Don't write the code; sketch the *shape*. Schema in pseudo-SQL is right; a 200-line TypeScript draft is wrong. The implementer will write the code; your job is the design.
- **Hand-waving "we should do X" without a phase plan.** "Migrate to Postgres" is a wish; "Phase 1 schema + seed, Phase 2 read swap, Phase 3 admin tools, Phase 4 removal — each ~half day" is a plan.
- **Vague trigger criteria.** "When needed" is not a trigger. "When admin edits content in prod and loses it" is. "When N% of search calls miss" is. Be specific or the issue rots.
- **No status check on a year-old issue.** If the issue is old, intervening work has probably moved the problem. Open with what's shifted. Skipping this means the proposal is solving the wrong problem.
- **Ignoring "no-gos."** Out of scope earns its line because *not naming* something invites scope creep. The implementer needs to know what NOT to build, not just what to build.
- **Treating shaping like PRD-writing.** A PRD spec's a product feature for a team. A shape proposal sharpens an open issue. Less prose, more direction. If your draft starts with "As a user, I want..." you're in the wrong skill — see `write-a-prd`.

## Calibration: what "good" looks like

A good shape proposal:
- Could be read in 2 minutes
- Names a direction strongly enough to argue with
- Has at least one piece of code-shaped concreteness (schema, file path, tool signature)
- Names ≥1 thing the implementer would otherwise step in (rabbit hole)
- Names ≥1 thing it explicitly won't do (out of scope)
- Names the trigger that should make someone pick it up

A bad one:
- Reads like a meeting summary
- Recommends "discuss further" or "options to consider"
- Contains zero concrete artifacts
- Treats every adjacent concern as in-scope
- Says "when ready" or "future work"

## Inputs from the user when ambiguous

When the user invokes the skill without specifying:
- **Which issue?** Ask. Don't guess from context unless the conversation has been about one specific issue.
- **How aggressive on the recommendation?** Default to opinionated. If the user later says "soften it" or "give me both sides," re-cast.
- **Appetite ceiling?** If the user hasn't said, infer from issue scope. A multi-quarter migration deserves a phase plan; a one-day fix doesn't deserve a proposal at all (auto-ship).

## When to skip into a PRD instead

A shape proposal is *adjacent to* a PRD, not a substitute for one. Punt to `write-a-prd` when:
- The work is a wholly new feature, not a sharpening of an existing direction
- User stories and acceptance criteria are the natural artifact
- A team will be reading it, not a single implementer
- The user explicitly asks for a PRD

A shape proposal lives on an existing issue and sharpens it; a PRD spawns a new artifact and decomposes into many issues.

## Reference: Shape Up's five elements, mapped to this skill

This skill's eight sections come from Shape Up's five pitch elements ([Basecamp / Ryan Singer](https://basecamp.com/shapeup/1.5-chapter-06)), adapted for the "proposal-as-comment-on-existing-issue" artifact:

| Shape Up | This skill | Why the adaptation |
|---|---|---|
| Problem | Status check (always — forces a codebase sanity-check) | Existing issue already states the problem; what's new is what's shifted since, and whether the claimed state still matches reality. |
| Appetite | Sequencing (per-phase rough size) | GitHub issues already have implicit appetite via labels; phase-level sizing is more useful for AI-agent execution. |
| Solution | Recommendation + What you'd build + What's NOT changing | Split: the recommendation is the one-paragraph version a busy reader needs; the sketch is for the implementer; the "not changing" call-out prevents incidental refactors that break the design's load-bearing assumptions. |
| Rabbit Holes | Rabbit holes | Same. |
| No-gos | Out of scope | Same. |
| — | When to pick up | Added — issues rot when triggers aren't named. |
| — | Related | Added — issues reference each other; the proposal should make that explicit. |
