---
name: codex-pr
description: Create a PR, review with `codex review`, fix issues in a loop until clean, then auto-merge. Use when the user says "/codex-pr", "review loop", "send it through codex", or wants to create and merge a PR with automated local code review.
---

# Codex PR Review Loop

Create a pull request, run `codex review` locally, address findings, loop until clean, then merge. Codex runs from the CLI on the user's machine — no waiting for a remote bot, no GitHub-side automation, no extra cost beyond the codex tokens.

## Steps

### 1. Pre-flight
- Run `git status` and `git log --oneline main..HEAD` to confirm what's being shipped
- If there are unstaged changes relevant to the PR, ask the user what to include before committing
- Confirm the branch is pushed to origin (push with `-u` if not)

### 2. Create the PR
- Use `gh pr create` with a concise title (under 70 chars) and a body containing:
  - `## Summary` — bullet points of what changed
  - `## Test plan` — checklist of verification steps
  - Footer: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- Use a HEREDOC for the body to preserve formatting
- Note the PR number from the output

### 3. Run codex review
- `codex review --base main 2>&1 | tee /tmp/codex-review-N.log` (use a per-round filename so logs aren't clobbered)
  - If the PR's base branch isn't `main`, swap accordingly: `--base $(gh pr view <number> --json baseRefName --jq .baseRefName)`
  - Codex executes locally and prints its findings to stdout when finished
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
- **Return to step 3** — re-run codex review against the updated branch
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
- **Cost-aware.** Each codex review run uses tokens. The judgment gate is the cost control: stop when marginal severity drops below worth-fixing.
- **Extract owner/repo dynamically** with `gh repo view --json nameWithOwner --jq .nameWithOwner` rather than hardcoding when constructing API calls.

## When NOT to use this loop

- The PR is too small to warrant a review pass (e.g. a typo fix). Just merge directly.
- The user wants the change reviewed by a human reviewer, not by an automated tool.
- The user has explicitly said "ship it without review."
