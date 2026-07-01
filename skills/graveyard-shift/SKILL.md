---
name: graveyard-shift
description: Work through the open issue backlog autonomously. Auto-ship the small clean fixes, prep draft PRs for review on bigger ones, file refined proposals when design choices need user input. For unattended sessions where the user is sleeping / away and wants to wake up to a productive set of changes.
---

# Graveyard Shift

The user is away (asleep, in a meeting, on a flight) and wants you to drain the issue list while they're gone. You triage each open issue into one of four buckets, execute the cheap ones end-to-end, prep prototypes for the design-laden ones, file proposals for the wholly-undecided ones, and surface a clean inventory when they return.

The user reviews the queued material when they're back. The skill's job is to maximize what they wake up to — not to make every call themselves.

## Scope: the whole list, until they're back

**The scope of a graveyard shift is the entire open issue list — minus the `priority:someday` tier. Full stop.** Not one epic, not one theme, not "the campaign we've been discussing." A theme or epic mentioned in recent conversation is a *starting point* for sequencing — it is never a *boundary*. The only thing that narrows scope is the user explicitly naming a scope **in the graveyard directive itself** ("just do the perf issues tonight"). Absent that, every open issue gets triaged into a bucket and every actionable bucket gets executed. (A real shift failed this way: it executed one 15-item epic, declared victory after a few hours, and left 70+ open issues untouched. The user's verdict: "You had plenty of time. It's a fucking graveyard shift.")

**`priority:someday` is excluded by default — even from "do it all."** The someday tier is deliberate parking: design forks the user has chosen not to engage yet (e.g. the product name #144, the stream-halt clarify architecture #261), and long-tail nice-to-haves. These are NOT in scope for a graveyard sweep — not as auto-ships, not as preps, not as proposals, not even as "while I'm here." A directive to "do everything / do it all" still excludes them; "everything" means the actionable backlog, and someday is by definition not-yet-actionable-by-choice. The user pulls someday work in **only by calling it explicitly** — by issue number, by the someday label ("drain the somedays tonight"), or by naming the specific item. Touching a `priority:someday` issue absent that is overstepping: you're un-parking something the user parked. The one exception is a *read-only* glance to confirm an in-scope issue isn't secretly blocked on a someday — that's triage, not work. (Do NOT re-file in-scope work as someday to dodge it, and do NOT promote someday work to in-scope on your own judgment — the tier boundary is the user's call, mirroring the product-name lesson: parked-vs-live is theirs to set.)

**The termination condition is the backlog or the user — never the plan.** "My planned batches are done" is not done. When a wave of subagents returns, the next action is **re-triage**: go back to `gh issue list`, pick the next wave, fan out again. Loop until (a) every open issue has been auto-shipped, prepped, proposed, or explicitly skipped per the buckets below, or (b) the user is back. If you stop early, you are deciding the user's backlog doesn't deserve the hours they gave you.

**Keep the fleet saturated.** Don't run one batch and wait for stragglers — when a subagent returns, spawn the next item from the queue into the freed slot (work-stealing, not batch-and-wait). A shift that finishes in 45 minutes with open issues remaining didn't finish; it under-scoped.

**Caps are per-bucket, not per-shift.** The 3–5 figure below caps *draft PRs awaiting morning review* (a human-attention budget). It does NOT cap auto-ships or proposals — those are unbounded; merged PRs and shaped proposals cost the user nothing in the morning. Never let the prep cap leak into "we've done enough tonight."

**Start of shift: sweep the stale-draft queue first.** Before triaging new work, inventory unmerged draft PRs and queued decisions from *prior* shifts (`gh pr list --draft` + the previous brief). Any draft that fixes a bug the user keeps hitting live goes at the TOP of the new brief ("you will keep hitting X until you review PR #N") — and if the user has since said anything that amounts to approval, land it. Fixes rotting in an unreviewed-drafts queue while the user re-experiences the bug is the single worst outcome a shift can hand back.

**Then sweep the observation register.** Right after the stale-draft sweep, pull `gh issue list --label observing` (the `observation-mode` skill owns the full contract). For **each** observing issue, **run its Signal source query and record the dated reading as a note on the issue** — adjudication is mechanical ("ran `<query>`, got `<reading>`, vs threshold `<X>`"), not a vibe check:
- reading at/under threshold and past the review-by → **graduate** (close, label `regression-candidate`);
- reading over threshold → **regression** — route it into the wave as a fix, with the contract's "watch for" giving diagnosis a head start;
- still inside the window → leave it, and carry its **age + last reading** into the brief ("#N observing 9d, watching X, last reading: 0 hits as of 6/30").

For a non-instrumentable observation issue (the carve-out — planning/eval/doc/copy work) the "query" is checking the named non-code channel (e.g. `gh issue list` for a follow-up, the user-report inbox) against its threshold; record that reading the same way.

**Also at start of shift: sweep the running register (`gh issue list --label running`).** These are live cross-shift jobs a prior shift (or a live session) launched that may still be executing — a long eval, a training run, a remote agent, a background build. They are the held resources and live actors you must not collide with. For each `running` issue, read its body (entry shape in [`docs/knowledge-homes.md`](../../docs/knowledge-homes.md) → "The running register"):
- **Treat its `Holds:` line as occupied.** Don't launch work that contends for that resource (the GPU it's holding, the model it has resident) and don't re-run a cell already in flight. A still-running job is the trigger for this whole register — rhdeck/local-ai-comparison#37 was a real eval holding the GPU with no GitHub record, so a shift could blindly collide with it.
- **Check the heartbeat for staleness.** A fresh heartbeat → leave it running and note it (in the brief, and to `shift-change`) as an **in-flight actor with age — NOT a decision awaiting the user** (a still-running eval is not a fork). A heartbeat gone stale past the threshold → flip the read to "investigate — possibly dead": follow its `Reap:` line to check real status, and **reap it** (close the issue, noting the freed resource) only once you've confirmed it's actually done or dead. Reaping is a confirmed decision, never an automatic kill.

**Optional sweep: orphan overview pages.** If a bulk Project-Overview seed happened recently, reconcile unfilled overview pages against open `graveyard-infra` fill-issues per repo — an unfilled page with no driving issue (or an issue with no page) is an orphan to repair. Full procedure in [`setup-graveyard-project`](../setup-graveyard-project/SKILL.md) → "Maintenance: the orphan audit".

**When a shift launches a long-lived async job, register it.** Any background process, remote agent, build, or eval that will outlive the moment you launched it gets a `running` issue *at launch* — one issue per job, carrying the `running` label and the entry shape from `docs/knowledge-homes.md` (What / Where / Holds / Output / ETA / Reap / Heartbeat). Heartbeat it as the fleet next touches it; close it on completion noting the resource freed. This is what makes the next shift's running-sweep above non-empty — register at launch so a later shift (or live human) can find the live actor without your transcript.

## The orchestration model: fan out, stay lean

This is the other load-bearing principle, and it is what keeps an overnight sweep affordable. A graveyard directive is an **explicit opt-in to parallel orchestration** — do NOT grind through items linearly in one ever-growing conversation.

**Why this matters (the cost mechanic).** Every turn in the main thread re-bills the *entire* accumulated context as input. A long linear session therefore grows cost **super-linearly**, and a single iterative grind — build → codex-review → fix → repeat, run 13× — is catastrophic, because every later round re-reads all the earlier rounds. The expensive iteration must never accumulate in the main context. (A real shift ballooned precisely because one PR's 13-round review loop ran inline in the orchestrator thread.)

**Pace against the active harness budget — see the `credit-pacing` skill.** A graveyard run is exactly where overage happens: nobody's watching the meter. At start of shift and before each new fan-out wave, identify the **current harness** first: Codex/OpenAI when this session is running in Codex, Claude when it is running in Claude Code, or another named harness when the user says so. Gate the orchestrator only on that active harness's budget; do **not** block a Codex run because Claude is tapped, and do **not** block a Claude run because Codex is tapped. If the budget tool prints multiple pools, treat inactive pools as informational only.

For review loops, also check the review engine's pool because `codex-pr` may spend Codex or fall back to AGY. Run any review loop with `BUDGET_FAIL_CLOSED=1` so a stale/missing Codex reading defers to AGY instead of spending blind. When the active harness or review engine is tapped, **schedule the gated work for that window's reset and keep working everything else**; never grind another round into overage. If the user corrects the budget reading or says the current data is stale, re-run the check and report the active-harness numbers explicitly before using budget as a constraint.

## Mode boundary: live brain vs. graveyard fleet

When the user is actively talking with you, the main thread is the high-context thinking surface. Use it for judgment, synthesis, architecture choices, live debugging with the user, and deciding what the next autonomous wave should be. Do not burn that shared context on repetitive implementation loops.

When the user says **graveyard shift**, the main thread changes jobs. It becomes the orchestrator, not the worker. If no worker agents have been spawned, a graveyard shift has not started; at most, you have done triage.

At the start of every graveyard shift, write down the concurrency plan before touching issue code:

- active harness and budget reading, plus the review engine budget if review loops will run
- repo, base branch, and any dirty-worktree constraints
- backlog source command and excluded labels/scopes
- worker slots available now
- first wave: issue number, bucket, expected output, and worktree/branch name per worker
- what remains intentionally in the main thread because it is serial or user-facing

Then fan out the first wave. The first wave should contain real worker agents for auto-ship, prep, or proposal work whenever such items exist. Explorer-only triage is not enough unless the backlog itself is still unknown.

Worker prompts should be small and disposable. Give each worker only the repo, issue URL/number, bucket, acceptance criteria, branch/worktree instructions, required tests, review-loop expectations, and final report format. Do **not** paste the accumulated live conversation into workers unless one sentence from it is actually acceptance criteria. The goal is for each worker to spend against the issue and repository state, not against the main chat transcript.

The main thread may do only these serial tasks during the shift:

- choose the next wave and keep worker slots full
- resolve true judgment forks that workers surface
- perform live browser/app/desktop checks that cannot safely parallelize
- publish the shift report and terminal summary

If you catch yourself implementing an issue, fixing tests repeatedly, or running a review-until-clean loop in the main thread, stop and move that work into a worker. Inline work is allowed only for tiny orchestrator maintenance that unblocks the fleet itself, such as fixing a broken script used to launch workers.

**The decomposition.** Break the backlog into **isolated subagents** — one per independent item (or a single `Workflow` for the whole fan-out). Each subagent gets:
- its **own context** (the grind happens there and is discarded when it returns),
- its **own memory space**, and
- its **own git worktree** (so parallel edits don't collide).

Each subagent does the full loop — implement → tests/tsc clean → codex-review-until-clean → open PR — and returns **only a PR + a short report**. Independent items run **concurrently**, not sequentially: faster wall-clock *and* far cheaper.

**ALWAYS delegate "loop until clean" to a subagent.** Anything that iterates — review-until-codex-clean, fix-until-tests-pass, harden-against-adversarial-cases — returns one summary, not N rounds. Running that loop in the main thread is the single biggest cost mistake.

**The orchestrator (main thread) does only four things:** plan the decomposition, spawn the agents, collect the PRs + reports, and synthesize (the final serial live-verification that genuinely can't parallelize — one app window, one set of credentials — plus the end-of-shift brief). It stays flat regardless of how many review rounds each item takes.

**Durable handoff is what makes this lossless.** The handoff substrate is **durable state — GitHub issues + repo docs + Notion overview — never the chat.** Before the run ends, every item's state lives in its issue, and any durable project knowledge lives in the repo docs or the Notion overview. That is what lets the session be cleared and resumed with nothing more than "get going on #N": the context that mattered is on disk in the system of record, not in a transcript. Treat the transcript as disposable; treat the issue/docs/overview as the system of record.

**Durable knowledge goes to git/Notion, NEVER local memory.** Local memory is a thin accelerant for the current task — ideally ~zero for a mature project — not a source of truth. Anything load-bearing belongs in a repo doc or the Notion overview, where it is versioned, visible, and cold-resumable. (Skills Manager learned this the hard way: ~16 local memory files had quietly become a parallel, invisible knowledge base shadowing GitHub + Notion — the exact anti-pattern to avoid.) For the full model — the four knowledge homes and the externalization lifecycle that puts a project on this footing — see [`docs/operating-model.md`](../../docs/operating-model.md).

**Reserve the main thread for two things only:** (1) live, interactive work *with the user* (necessarily linear), and (2) serial live app/desktop driving that can't parallelize (one window; the OS targets the app by process name, so two binaries collide). Everything else belongs in an isolated agent.

## The contract: decisions, never confirmations

This is the load-bearing principle. The user's morning attention is for **decisions** — judgment calls only they can make. It is NOT for confirmations — "is this fix right?", "should I merge?", "does this look ok?". Those are answerable by other AIs (codex review, type-checkers, the build) without spending the most expensive resource.

**The review loop IS the second opinion.** Run it on every PR before merging — via the **`codex-pr` skill's loop**, which owns *how* to review. Do NOT call `codex review` directly from here; that duplicates the codex-pr skill and hardcodes a single pool. The codex-pr loop is budget-aware: it routes to Codex while it has quota and falls back to AGY (`agy`, Gemini) when the Codex pool is exhausted, so a sweep never stalls on a maxed Codex limit. No findings or only nits → ship. Substantive findings → patch them, also without asking. The user does not need to re-validate work the review already validated.

**Default to shipping.** If the review passes, type/cargo check passes, the diff is on-policy: merge. Do not queue "want me to merge?" Do not pre-announce intentions like "I'll patch #X then check #Y then ..." — those are confirmation-seeking dressed as status updates. Just do the work and report what landed.

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
4. Open PR, run the `codex-pr` review loop (budget-aware engine, judgment gate, stopping rules)
5. Merge when clean (or stopping window hit with only manageable P2s — apply silently per skill exception and ship)

**Ship-into-observation is part of the diff, not a follow-up.** When an auto-ship lands judgment-shaped work that wants watching, the worker reopens with the `observing` label and the observation contract (see the `observation-mode` skill) — and the **Signal source must be instrumented in the same PR**: if "watch for X" needs a log line/counter/metric production doesn't emit, the worker *adds it in this diff* and fills the Signal source field (artifact + query + threshold). A contract the worker cannot make queryable is the signal to route the item back to **prep** instead, exactly as a failed eligibility gate does. (Non-instrumentable work — copy/doc/eval — uses a concrete non-code signal source per the carve-out in `observation-mode`; don't manufacture a metric for a trivial change whose revert is free.)

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
- Observation tasks (user has to look at logs) → still useful to file a proposal naming the **signal source** (the production artifact, the query that reads it, and the threshold) and WHEN to read it; that's not skip, it's a sharpened observation issue
- Speculative bug fixes for unobserved shapes → `shape-an-epic` with explicit "When to pick up" naming the observable signal and where it'd be queried
- Issues blocked on a parent that requires user approval → check if you can land the parent's *unblocked* child first; if not, `shape-an-epic` the parent so the approval gate is concrete

Skip should fit in a short list at the end of the summary. If skip is more than ~25% of the backlog, you're skipping things that wanted shaping.

## Execution order

The orchestrator plans the decomposition, then **fans the action buckets out to isolated subagents** (per "The orchestration model" above) and collects results. The passes below describe *what* each item routes to — not a serial single-thread crawl. Independent auto-ships and preps run concurrently; the orchestrator stays lean and synthesizes.

Proposals are not the slow tail. They ship as eagerly as auto-ships — they're cheap (one comment per issue, no codex loop) and they compound for the user's morning review:

1. Auto-ship pass: **one subagent per item** (own worktree + context), each running its own implement → codex-clean → merge loop and returning a PR + one-line report. The user wakes up to N green merges; the review rounds never touched the main context.
2. Prep pass: 3-5 draft PRs is a productive morning of review. More than that and the user can't get through them over coffee. (Also subagent-per-item.) This caps the *drafts*, not the shift — if prep slots are full, route remaining prep-shaped items to proposals and keep going.
3. **Proposal pass: shape every epic-shaped issue you can.** Use `shape-an-epic` aggressively. Each proposal is 15–25 minutes of focused thinking; ten of them in a night is a transformed backlog. The user has a bias toward motion — 80%-good-enough proposals are the artifact that lets the next pass be a refinement, not a from-scratch.
4. Skip pass: note in the final summary, no action.
5. **Loop.** When a wave returns, re-run `gh issue list` and fan out the next wave into the freed slots. The passes above describe routing, not a one-shot plan — repeat until the backlog is drained or the user is back (per "Scope" above).

Before declaring the shift done, confirm the **durable handoff**: every item that landed or was queued has its state on its GitHub issue + repo docs + Notion overview (never local memory), so the session could be cleared and resumed losslessly. The brief and terminal summary (below) are the human-facing layer on top of that durable state.

Proposals are LOWER overhead than auto-ships (no PR, no codex loop, no merge) and HIGHER leverage on backlog clarity. Don't sandbag this pass.

## Triage gotchas

- **Stale diagnoses.** Old issues may describe problems already partially fixed by intervening PRs. Read the issue, then verify against current code before believing the diagnosis. Surface stale findings as a refined-proposal comment.
- **Dependencies.** If issue A is blocked on issue B (B needs user approval), do B's child issues first if they unblock the bigger arc. Don't paint yourself into corners requiring approvals you don't have.
- **Codex round budget.** Auto-ship items can chew 4-6 codex rounds. Don't keep pushing a single PR past round 8 — that's the architecture telling you the diff is wrong. Stop, file follow-ups, surface to user.
- **Worktree node_modules.** Worktrees off `origin/main` need their own `node_modules` (or a symlink to a recently-installed one in another worktree). The first worktree of the night usually pays the install cost; later ones can symlink.

## What "ready" looks like at the end

**Two artifacts, both mandatory:**

### 1. A fresh dated Shift Report — published to **Notion**, not a local file

**Publish the shift report to the shared Notion "Briefs" database** via the project-neutral CLI, not a local markdown file. (The old `test-plans/graveyard-brief-*.md` approach scattered reports across gitignored worktrees with no shared history — don't do that anymore.) One database holds reports across **all** projects, newest-first, tagged by project; the user reviews and iterates on the published page.

**Before publishing: diff against the prior Active report (the cross-brief review).** A shift report is the next entry in a *conversation*, not a standalone snapshot — its value is the relationship to the one before it. Pull the previous Active report and read it against what this shift actually did:

```bash
# find the prior Active report for this project (the one you're about to supersede)
python3 ~/.config/ai-briefs/notion_briefs.py list --project "<Project Name>" --status Active --type "Shift Report"
```

Then reconcile, and let the new report reflect the answers:
- **Did this shift undo anything the prior brief established?** A decision recorded as settled, a fix that landed, a direction the user approved — if tonight's work reverses or contradicts it, that's the single most important line in the new report. Call it out explicitly; don't let a silent regression hide in a fresh snapshot.
- **What decisions has the user since made?** Forks the prior brief surfaced that have since been answered (on the issue, in a shift-change, in conversation) are *resolved* — reflect the outcome, do NOT re-surface them as open. Re-asking a settled question is the brief's worst failure.
- **Is it consistent?** The two reports should tell one coherent story. If the prior brief said "X is blocked on Y" and Y shipped, the new one says so. Contradictions between consecutive reports mean one of them is wrong — find which.
- **What's being pulled forward?** Carry-forward comes from two sources: open GitHub issues/draft PRs (reality), AND the prior brief's own unresolved decision section (the conversation). Both feed the new report. A reader comparing report A and report B should be able to see, line by line, what moved, what landed, and what's still waiting — that A→B legibility is the point.

Procedure — write the report to a temp markdown file, confirm the project pick-list, then publish:
```bash
# 0. confirm the project name matches an existing pick-list option (avoid typo-dupes that split history)
python3 ~/.config/ai-briefs/notion_briefs.py projects
# REPORT=/tmp/shift-report.md  (write the dated report here, current-state + cross-brief reconciliation above)
python3 ~/.config/ai-briefs/notion_briefs.py publish \
  --project "<Project Name>" \        # match an existing option EXACTLY; a new name registers a new project
  --date YYYY-MM-DD \
  --title "Shift Report YYYY-MM-DD" \
  --type "Shift Report" \
  --status Active \
  --file "$REPORT"                     # prints the new page URL — hand it to the user
# supersede the prior Active report via the CLI (its unresolved items now live in the new one)
python3 ~/.config/ai-briefs/notion_briefs.py set-status <prior-report-url> --status Superseded
```
The tool converts markdown → Notion blocks and returns the page URL. Setup/details live in `~/.config/ai-briefs/README.md`. If the publish fails (no DB configured, token/connection problem), surface it and fall back to a local file ONLY for that one shift, then fix the config.

The report reflects **current** state. A report whose date doesn't match today's repo is worse than none — it actively misleads. You do NOT delete prior reports (the database keeps the dated history); instead the **newest report is the canonical current-state one** (Status=Active; supersede the previous), and the carry-forward rule below still governs what it must contain.

**The brief is about STATE, not about the shift.** Its job is "this is what's open in front of you" — the complete current set of decisions and approvals waiting on the user — NOT a report card for tonight's work. A decision queued by a *previous* shift that the user never resolved (a draft PR awaiting review, a live test never run, a fork never answered) MUST reappear in tonight's brief, marked with its age ("draft #N, waiting since 6/10 — you will keep hitting bug X until this lands"). "It was in the last brief" is hiding the ball: superseded briefs are how pending items vanish. Build the decision section by sweeping reality, not memory: `gh pr list --draft`, open PRs authored by agents, the prior brief's decision section, and any issue marked as awaiting the user. Every item is either resolved, carried forward, or explicitly retired with a reason — never silently dropped.

**Rules for the brief (now a Notion Shift Report):**
- One report row per shift, dated (its own page in the Briefs database). Prior reports stay as dated history — do NOT delete them; mark them Status=Superseded. The newest report is the canonical current-state one (Status=Active); *unresolved items always carry forward into it* per the state rule above (so a reader never has to dig through old reports to find what's still open).
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
- **Every queued draft PR carries its own What / Why / Decision IN THE BRIEF — not just a link.** A PR row that says only "PR #27 — de-binarized scoring — confirm the metrics" forces the user to open the PR and the issue to reconstruct what they're deciding. That's the failure mode: the brief should let the user 80/20 the call *from the brief itself*, diving into the PR only when they want the deep version. So give each queued PR three tight beats:
  - **What it is** — one or two sentences describing the change concretely (what the diff does, what now exists that didn't).
  - **Why it exists** — the problem it answers and the evidence that prompted it (the issue, the measured finding, the bug the user kept hitting). Make the motivation legible without the issue open.
  - **The decision** — the specific fork being handed back, stated as a fork with a recommendation ("I pinned X; the alternative is Y; I recommend X because Z — your call is just confirm-or-flip"). If there's genuinely nothing to decide, it's not a queued-decision PR — it's an auto-ship; merge it.
  The PR's own "Things to push back on" section is the deep-dive; the brief's What/Why/Decision is the executive layer that stands alone. A reader who only reads the brief should be able to approve or redirect every PR without clicking through. (This came directly from the user: "I'm looking at these and not quite tracking it… I have to dive deep into the PR or the issue to learn more. Put more into the brief so I can 80/20 it.")
- Status of completed work is a one-liner table at most. The user doesn't need a play-by-play.
- "What I'm doing without you" is a first-class section, not an afterthought. List the calls you took back (sequencing, shaping, clean merges) so the user sees you're *running*, not stalled. The brief's two jobs are: **(1) catch the user up, (2) extract the few genuine forks.** Everything between those two is work you should already be doing.
- "Items NOT requiring a decision" / cleanup (locked worktrees, stale files) goes at the bottom and stays small. If it's truly trivial, just do it instead of mentioning.
- **If the project accumulates large *reclaimable* artifacts (model weights, datasets, build/output caches, worktrees), surface a storage line AND ask the dormancy question.** Disk is the resource analogue of credits — an unattended run is exactly where it silently fills. Two parts: (1) state current free space + the biggest reclaimable rocks; (2) ask **"are we putting this down for a while?"** — because the right aggressiveness is dormancy-dependent. *Staying active* → keep the working set warm (champions/current-round artifacts resident) so iteration stays fast; evict only redundant/also-ran/duplicate artifacts. *Going dormant* → prune hard toward near-zero and re-fetch on resume. The durability contract is provenance (a manifest of how to recreate each artifact), not the bytes — so eviction is reversible and costs only re-fetch *time*, never the asset. Never auto-delete artifacts the project didn't create (a user's unrelated models/data on the same machine) — flag those, don't evict them.

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

**The brief is the agenda for the next `shift-change`.** The two skills form the primary development loop: graveyard shift (autonomous, away) produces the decision queue; shift change (live, with the user) drains it, grooms the backlog on GitHub, and cues the next graveyard shift. Write the brief so a shift-change session can open from it directly — every pending item resolvable, none requiring archaeology.

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
