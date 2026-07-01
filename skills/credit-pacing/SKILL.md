---
name: credit-pacing
description: Check AI credit/budget before spending it, and pace work around overage instead of chomping into it. Use before any costly engine call (Codex review, codex exec, long main-thread loops), whenever the user says "pause / wait for credits / we're out of credits / hold off until reset," and at the top of any graveyard/unattended run. Turns "pause" into "gate that one path, keep working" and turns overage into a scheduled wait for the window reset.
---

# Credit Pacing

Don't spend credits you don't have, and don't stop working just because *one* pool is tapped. This skill is the policy for **checking budget before a costly call** and **pacing around a tapped window** — so an unattended run never chomps into overage, and a "pause" never becomes a stall.

It exists because the previous wiring (`codex-pr`'s `pick-review-engine`) **failed in three ways** and let a graveyard run blow past 100%:

1. **Failed open.** No CodexBar data, or *stale* data → it defaulted to Codex and spent blind — exactly when monitoring was down.
2. **Guarded one wrapper only.** It picked an engine for `review main`, but direct `codex`/`codex exec` calls, and **the entire Claude-side cost of an iterative loop**, were ungated. The 13-round build→review→fix grind is what chomps credits, and nothing checked a budget before deciding to do *another round*.
3. **Could not stop.** Best case it switched engines; it never *halted* and never *waited for reset*. The pause-for-reset behavior the user actually wanted didn't exist.

This skill fixes all three: **fail closed when unattended, gate the decision to *continue*, and have a real wait-for-reset path.**

## The two-line check

Budget lives in CodexBar's on-disk cache (no network). The reader + chooser ship with `codex-pr`:

```bash
~/.claude/skills/codex-pr/scripts/budget            # human view: each window's used% + reset time
~/.claude/skills/codex-pr/scripts/pick-review-engine # prints codex|agy, gates on the same cache
```

`budget` prints both **CODEX** and **CLAUDE** windows. Read **both** — a long main-thread loop spends *Claude* credits, not Codex; the engine choice only governs Codex.

## Policy: before any costly spend

A "costly spend" = a Codex review/exec, **or** deciding to run another round of an iterative loop, **or** kicking off a fan-out of subagents. Before it:

1. **Run `budget`.** Identify the window the spend draws from (Codex review → Codex session/weekly; main-thread loop → Claude session/weekly).
2. **Classify the window:**
   - **Healthy** (< 90%) → proceed.
   - **Tight** (90–98%) → proceed only for the immediate task; don't start a new multi-round loop. Prefer the cheaper path.
   - **Tapped / overage** (≥ 98%, and especially ≥ 100%) → **do not spend on that pool.** Take the unattended or live branch below.
3. **Fail CLOSED, not open.** If there is **no CodexBar cache, or the latest `capturedAt` is > 30 min old**, treat the pool as *unknown → assume no headroom* when unattended. Stale data is not headroom. (The default scripts fail *open*; this skill overrides that for unattended runs — pass it explicitly, see below.)

## When a pool is tapped

**Unattended / graveyard (user is away):**
- **Schedule the gated work for the window's reset, and keep working on everything else.** `budget` prints `resets <Nh NNm>` and the raw `resetsAt` is in the cache. Use `ScheduleWakeup` (or a `Cron`) keyed to that reset time to resume the gated step. Meanwhile, do every task that draws on a *different* pool or no pool (file work, research, drafting, issues, ungated reviews).
- If a *different* engine is healthy and is a legitimate substitute (e.g. Codex tapped but AGY/Gemini has headroom and the task is a code review), **switch to it** instead of waiting — `REVIEW_ENGINE=agy review main`. AGY is also a valid second opinion (different model family).
- **Never** run another round of a loop on a tapped pool just to "finish." Defer the loop; the backlog will still be there after reset.

**Live (user is here):**
- Say it plainly: "Codex weekly is at 99%, resets in 3h12m." Offer the fallback (AGY) and/or defer. Don't block silently and don't burn overage by default — let the user choose.

## "Pause / wait" = gate that path, keep working

This is the behavioral half, and it's a hard rule (also in the user's global CLAUDE.md). When the user says **"pause Codex / wait for credits / hold off until reset"**:
- It gates **that one tool/path**. It is **not** a stop-work order, and you do **not** reply "ok, what should I do instead?" — that bounce is the stall the user's top principle forbids.
- Keep doing all non-gated work autonomously. Build testable artifacts.
- Only if *everything* left is behind that one gate: say "everything else is done; only <X> remains, gated until <reset>" — schedule it for the reset and still look for adjacent useful work. Don't ask to be re-tasked.

## Integration points

- **`codex-pr`** — its review loop should run this check *per round*, not just once: before each new round, re-run `budget`; if the Codex pool is tapped, stop the loop and either switch to AGY or schedule the remaining rounds for reset. The bundled `pick-review-engine` does the single-call engine choice; this skill governs whether to *keep looping at all*.
- **`graveyard-shift`** — at start of shift and before each new fan-out wave, run the check. A graveyard run must pace itself against *both* the Claude pool (its own loop cost) and the Codex pool (review cost), and defer-to-reset rather than overage. The cheapest insurance against a runaway-cost shift.

## The menu of smart moves (when a pool is tapped)

The point is **not** "stop." It's "don't spend *blindly* — pick the move that fits the situation." When Codex (or the relevant pool) is over budget, weigh these by **how long until reset** (the budget cache gives you `resetsAt`):

- **Reset is soon (≲45m):** just **wait**. `ScheduleWakeup` for the reset (or loop-retry every ~15m to see if quota freed up) and run it then. Waiting a few minutes beats both overage and a worse engine.
- **Reset is far (hours/days):** don't sit on it. **Switch to AGY** now (`REVIEW_ENGINE=agy review main`) — a real different-model second opinion — **or bank other non-Codex work** and revisit after reset.
- **Genuinely urgent and only Codex will do:** **override** consciously (`CODEX_BUDGET_OVERRIDE=1` prefixed on the command). Overage is a choice you can make on purpose; the goal is just to stop making it *by accident*.

The failure last night was none of these — it was ~8 Codex reviews munching quota already in overage, with zero consideration. *Any* of the moves above would have saved it.

## Hard enforcement (implemented) — the hook INFORMS, the agent DECIDES

Policy alone relies on the model remembering. Two mechanisms now back it — and the hook is deliberately a **soft interrupt**, not a wall: it pauses one naive call and hands back the two facts judgment needs (how over, how long until reset) plus the menu above. The agent stays in charge.

- **`pick-review-engine` fails closed on demand.** Treats `capturedAt` > 30 min as no-data; `BUDGET_FAIL_CLOSED=1` makes no-/stale-data fall back to AGY instead of spending Codex blind. Set it for unattended/graveyard review loops.
- **PreToolUse hook `~/.claude/hooks/codex-budget-guard.py`** (registered in `~/.claude/settings.json`, matcher `Bash`). On every Bash call it checks whether the command is a `codex` *spend* (exec/review/resume/fork/bare prompt). If a **FRESH** reading shows a window ≥ threshold (default 98%), it **interrupts that one call with a reset-time-graduated message** ("resets soon → wait" vs "resets far → take another path") — so a stray `codex` call can't chomp overage even if the model forgot. It **fails open** on no/stale data, never touches non-spend codex calls (login/doctor/mcp/apply/help), and is overridable per-call. Tune via `CODEX_BUDGET_BLOCK_THRESHOLD` / `BUDGET_SOON_MIN` / `BUDGET_STALE_MIN`. When you hit it, **read the reset time and pick from the menu** — don't just override reflexively.
