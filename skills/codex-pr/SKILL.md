---
name: codex-pr
description: Create a PR, review with `codex review`, fix issues in a loop until clean, then auto-merge. Use when the user says "/codex-pr", "review loop", "send it through codex", or wants to create and merge a PR with automated local code review.
---

# Codex PR Review Loop

Create a pull request, run a local review, address findings, loop until clean, then merge. The review runs from the CLI on the user's machine — no waiting for a remote bot, no GitHub-side automation.

**The review judges three dimensions, not just code.** Under the graveyard-shift model a PR doesn't just have to be correct code — it has to *solve the issue it's for* (and that issue may serve a broader concern), and it has to *keep documentation honest* so the next AI can pick up the code without reading the whole repo. So every pass evaluates:

1. **Code correctness / security / maintainability** — the engine's built-in pass.
2. **Issue fidelity** — does the change actually do the job the issue describes, correctly and completely, without solving an adjacent/narrower problem or drifting scope? This requires feeding the engine the issue (Step 1b).
3. **Documentation fidelity & drift** — is new/changed code documented enough (purpose + contract + non-obvious intent) for an AI to grok it locally, AND did this change leave any *nearby* docs stale — a function doc comment, a module/file header, an algorithm explanation, a referenced README/inline note that now describes behavior the diff changed? Stale docs left uncorrected are drift, and drift is a finding.

The rubric for dimensions 2–3 lives in `scripts/review` and is fed to whichever engine runs, so the `[P1]/[P2]/[P3]` judgment gate below is identical across all three.

**Engine is budget-aware — never hardcode `codex review` directly.** The review step goes through the `review` script **bundled with this skill** (`scripts/review`, alongside `pick-review-engine` and `budget`), so the mechanism travels with the skill. It chooses the pool: **Codex while it has quota, AGY (`agy`, Gemini) as the fallback** when the Codex weekly/session window is exhausted — so the loop no longer dies when the Codex pool is tapped. AGY is also a legitimate second opinion precisely because it's a different model family than the Claude that wrote the code. Both engines emit the same `[P1]/[P2]/[P3]` findings format, so the judgment gate below is identical regardless of which ran.

**One-time setup (per machine):** run `bash scripts/install.sh` to symlink `review`/`budget`/`pick-review-engine` onto your PATH. If they aren't on PATH, call the bundled copy directly: `"<this-skill-dir>/scripts/review" main`. Prereqs: `codex` and/or `agy` installed; CodexBar (macOS) provides live budget data but is optional — without it the scripts fall back to the default engine. Run `budget` to see remaining quota.

## Steps

### 1. Pre-flight
- Run `git status` and `git log --oneline main..HEAD` to confirm what's being shipped
- If there are unstaged changes relevant to the PR, ask the user what to include before committing
- Confirm the branch is pushed to origin (push with `-u` if not)

### 1b. Stage the issue context (so the review can judge issue fidelity)
The review can only check "does this solve the issue?" if it can *see* the issue. Identify the issue this PR closes and stage it into a context file the review engine reads:
- Find the issue number: from the branch's `.smartterm-issue` marker, the branch name (`#N`), a "Closes #N" in the PR body, or the work item that spawned the PR. If there's genuinely no issue (e.g. a pure refactor), skip this step — the review still runs, and the rubric tells the engine to say intent couldn't be verified rather than assume.
- Write the issue body + its key comments + the PR description to a file, and point the review at it:
```bash
ISSUE=<n>
{ echo "=== Issue #$ISSUE ==="; gh issue view "$ISSUE" --json title,body,labels \
    --jq '"# " + .title + "\nlabels: " + ([.labels[].name]|join(", ")) + "\n\n" + .body';
  echo; echo "=== PR description ==="; gh pr view <pr> --json title,body --jq '"# " + .title + "\n\n" + .body'; } \
  > /tmp/review-ctx-$ISSUE.md
export REVIEW_CONTEXT_FILE=/tmp/review-ctx-$ISSUE.md
```
- If the issue links a parent/epic ("part of #M", "tracked in #M"), append that parent's body too — the broader concern is part of what "doing the job" means.

### 2. Create the PR
- Use `gh pr create` with a concise title (under 70 chars) and a body containing:
  - `## Summary` — bullet points of what changed
  - `## Test plan` — checklist of verification steps
  - Footer: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- Use a HEREDOC for the body to preserve formatting
- Note the PR number from the output

### 3. Run the review (budget-aware engine)
- `review main 2>&1 | tee /tmp/review-N.log` (use a per-round filename so logs aren't clobbered)
  - `review` picks the engine by budget (Codex if it has quota, else AGY) and runs the pass against the base branch. It prints the chosen engine to stderr (`▸ review engine: …`).
  - It reads `REVIEW_CONTEXT_FILE` (staged in Step 1b) and feeds the issue + PR context plus the issue-fidelity & documentation rubric to the engine, so a single pass returns findings across all three dimensions. Keep that env var exported for every round of the loop.
  - If the PR's base branch isn't `main`, pass it: `review $(gh pr view <number> --json baseRefName --jq .baseRefName)`
  - To force an engine for a run: `REVIEW_ENGINE=codex review main` or `REVIEW_ENGINE=agy review main`
  - The engine executes locally and prints its findings to stdout when finished
  - Fallback if the wrapper is somehow unavailable: `codex review --base main` directly (only when Codex has budget — check `budget` first). NOTE: on codex-cli 0.133+ `codex review --base` cannot take a custom prompt arg (it's mutually exclusive with `[PROMPT]`), so this bare fallback runs codex's built-in pass WITHOUT the issue-fidelity/doc-drift rubric — use the `review` wrapper to keep all three dimensions.
- Findings come back tagged with severity in square brackets:
  - `[P1]` — must-fix red issue (blocks merge)
  - `[P2]` — yellow issue, should evaluate; sometimes fix
  - `[P3]` — minor / nit, optional

### 4. Apply judgment to the round's findings

This step is the judgment gate that separates "loop forever on diminishing returns" from "ship at the right moment." Decide what to do with the findings *before* fixing or looping:

- **Any P1?** Fix and re-loop. P1s block merge; no judgment call needed.
- **Only P2s?** Surface them to the user with your read on each. *"Codex flagged X. I think this is real / I think this is out of scope / I think this is a design tradeoff. Fix, ship as-is, or follow-up issue?"* Don't auto-fix P2s unless the user has previously waved them in for this PR or the fix is unambiguous and small.
- **Only P3s?** Include in the final summary, never trigger another round.
- **Empty review (codex returned nothing)?** Proceed to merge.

Calibration for the two non-correctness dimensions:
- **Issue-fidelity finding ("doesn't actually solve the issue / solves the wrong or narrower problem").** This is usually a [P1] and it is *not* always a small fix — it can mean the PR needs reshaping, not a patch. Treat it like structural surgery (per the boundary table): if the gap is clear and small, close it and re-loop; if closing it means materially redesigning the change, **stop and surface to the user** (in a graveyard run, kick the item from auto-ship back to a draft/prep with the gap named). Never merge a PR the review says doesn't do the job the issue describes.
- **Documentation / drift finding.** A stale doc comment, an out-of-date module header, or a missing doc on complex new code is almost always a small, unambiguous fix with no design choice — so it falls under the "P2 with an obvious one-line fix" exception: **apply it silently and mention it**, don't ping the user. The point of the dimension is to keep docs from drifting as code changes; fixing the drift in-loop is exactly the intended behavior. Only surface a doc finding as a real decision if "what the code should do" is itself unsettled (then it's an issue-fidelity question, not a doc one).

Stopping rules — invoke any of these to stop the loop and surface to the user:

- **Two consecutive rounds with no P1s** → stop. Diminishing returns. Surface the cumulative P2s (if any) and ask: ship, fix more, or open follow-ups.
- **Findings/round drops below 2 for two consecutive rounds** → stop. Same reason.
- **Same finding recurs after a fix** → stop and investigate. Either the fix missed, codex is misreading, or the issue is subtler than it looks.
- **Round count > 8** → stop. The diff is probably too big and needs human eyes; recommend splitting the PR.

### 5. Report findings (every round)
- Show the user the codex output verbatim (or a tight summary if it's huge), grouped by severity
- For each finding, give your read: "I think we should fix this", "this is pre-existing and out of scope", "this is a design choice"
- For P2s under judgment gate: ask explicitly. Don't silently fix.
- Be honest about diminishing returns — if codex just found one P3 nit, say "this is the floor; recommend stopping."

### 6. Fix issues (when warranted) and re-review
- For each finding that should be fixed:
  - Read the relevant file, understand the issue (don't just take codex's word — verify first)
  - Make the fix
- Commit with a message that references codex round and severity (e.g., `fix: address codex round N — [P1] short description`)
- Push the commit
- **Return to step 3** — re-run `review` against the updated branch
- Continue per the judgment-gate rules in step 4

### 7. Auto-merge when clean
- Once any of these is true:
  - Codex returned an empty review
  - The only outstanding findings are P3 nits
  - The user has explicitly waved off remaining P2s
- Then merge:
  - `gh pr merge <number> --squash --subject "<PR title> (#<number>)"`
  - `git checkout main && git pull`
- Report the merged PR URL

## Important

- **Never merge over outstanding P1 findings.** The judgment gate doesn't let P1s through.
- **P2s require user judgment.** Auto-fixing them silently throws away the user's right to choose "ship now, follow up later." The exception: a P2 with a one-line, obviously-correct fix and no design choice is fair to apply silently and mention.
- **Verify before fixing.** Codex sometimes flags things that look like bugs but are intentional. Read the code, decide if it's a real issue. Don't blindly apply suggested fixes.
- **Track findings per round.** If the trend is dropping (4 → 2 → 1), call it out — that's the natural stopping window.
- **Codex respects committed state.** It reads your branch state via git, not the live filesystem — push before review for an accurate read.
- **Cost-aware.** Each review run draws tokens from the chosen pool (Codex or AGY). The judgment gate is the cost control: stop when marginal severity drops below worth-fixing. Run `budget` if you want to see what's left before a long loop.
- **Extract owner/repo dynamically** with `gh repo view --json nameWithOwner --jq .nameWithOwner` rather than hardcoding when constructing API calls.

## When NOT to use this loop

- The PR is too small to warrant a review pass (e.g. a typo fix). Just merge directly.
- The user wants the change reviewed by a human reviewer, not by an automated tool.
- The user has explicitly said "ship it without review."
