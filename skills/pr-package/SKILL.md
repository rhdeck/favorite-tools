---
name: pr-package
description: Open a pull request as a decision package — summary + inline content for review + explicit "things to push back on" + test plan with checkboxes + Closes #N — so the user reviews ONCE with every load-bearing call surfaced. Use whenever you are about to open a PR, draft a PR body, write a commit message that will become a PR, or update an existing PR description. Also use proactively when you finish a change and a PR is the obvious next step.
---

# PR Package

Standard shape for pull requests. A good PR isn't a code dump — it's a decision package. The user reviews once; every call you made that they could redirect should be visible.

## When to use

- Opening a new PR.
- Updating the body of an existing PR after material changes.
- Writing a commit message that you know will become a PR (squash-merge workflow).
- Splitting a PR (one shippable, one parked) — both halves get the package.
- Marking a PR as parked / blocked — the body gets a status section.

## The required PR body shape

```markdown
## Summary

- [1-3 bullets: what changed, why, in 1 sentence each]

[For content-heavy PRs: INLINE the content here for review — JSON schemas, prose excerpts, config snippets. Never link to a sidecar file the user has to bounce to.]

## Things to push back on

- **[Decision 1]:** [the call you made + the alternative you considered + the reason you chose this. Make redirecting cheap.]
- **[Decision 2]:** ...
- **[Decision 3]:** ...

## Scope cap (optional, when the PR could have grown)

- [What this PR deliberately does NOT change]
- [Why that boundary]

## What [user] should look at first

[Optional: 1-3 ordered items. Most useful when the diff is large or content-heavy.]

Closes #[N]

## Test plan

- [x] [Test that ran and passed]
- [x] [Another test that ran and passed]
- [ ] [Test the user needs to run / decision the user needs to make]
- [ ] [codex-pr review round, if code change]

[Draft until the codex-pr review passes + user's eye if his-eye-required.]
```

## The non-negotiable rules

1. **"Things to push back on" is REQUIRED on any PR with non-trivial decisions.** Don't ship a PR that only describes WHAT changed. Surface the choices you made that the user could reasonably redirect. Each item = the call + the alternative + the why.

2. **INLINE content for review.** If the PR adds JSON files, markdown content, prompt text, copy, schema — render the content inline in the PR body. Do not link to a `.json` or `.md` file and ask the user to bounce. The PR body IS the rendered view. (See memory: `feedback_inline_structured_content`.)

3. **Closes #N** — every PR references the issue it closes. Squash-merge then auto-closes. If the work doesn't have an issue, file one first (small ≠ disposable, see CLAUDE.md + `feedback_github_issues_not_todos`).

4. **Test plan with checkboxes.** Use `- [x]` for done, `- [ ]` for what still needs to happen. Make the gating items obvious.

5. **Clickable file paths** when referencing files in the body: `[path](file:///abs/path)`, NOT code-tag spans. (See memory: `feedback_clickable_file_links`.)

6. **No emojis** in the body or commit message body unless the user has explicitly asked.

7. **Co-Authored-By trailer** on commit messages:
   ```
   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   ```

8. **Heredoc for commit messages and PR bodies** when passed via `git commit -m` or `gh pr create --body` to preserve formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   subject line

   body paragraph with proper wrapping.

   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   EOF
   )"
   ```

## Decisions you make on the user's behalf (state them)

The PR package is itself a decision bundle. Before opening, decide each of these and surface them as either commits, body content, or "things to push back on":

- **Worktree → branch → PR → issue chain.** New work spins a worktree off `origin/main`, named after the topic (not generic; see `feedback_worktree_naming`). Branch follows. PR follows. Issue exists first or gets filed.
- **Selective commits.** Don't `git add .` or `git add -A`. Stage specific files. Discuss what to include with the user before bulk-committing untracked files. (See memory: `feedback_selective_commits`.)
- **Draft vs ready.**
  - Draft if: the codex-pr review hasn't run on code changes, user's eye required for content/voice, blocked on external decision.
  - Ready if: tests pass, decisions self-contained, no `his-eye-required` flag.
- **Split or bundle.** If a PR mixes shippable code with parked content (the recent `#230` split), CARVE IT — ship the shippable, park the rest in a sibling draft with a clear `blocked:` label. Don't let parked content hold up shipped value.
- **Park-not-close for blocked drafts.** When a draft is waiting on the user's voice pass, design call, or external dependency: label it (`blocked: voice-pass`, `blocked: <topic>`), update the body with a "Status: PARKED" section explaining what unblocks it, and leave it visibly waiting. Do NOT close it — ideas stay. (See `feedback_research_brief_pattern` for the related synthesis rule.)
- **codex-pr review loop** for code changes. For pure content / docs PRs, skip codex (no correctness surface).
- **Don't merge his-eye-required drafts.** Build them aggressively; let the user click merge. (See `feedback_aggressive_overnight_drafts`.)

## Workflow

### 1. Set up the chain

```bash
# In primary worktree:
gh issue view <N>  # confirm the issue exists or create it first
git worktree add -b feat/<topic-name> /Users/ray/Documents/<repo>/.claude/worktrees/<topic-name> origin/main

# Work in the worktree. Selective stage. Commit with heredoc + Co-Authored-By.
```

### 2. Draft the body BEFORE running `gh pr create`

Write the body to a heredoc variable or temp file first so you can see the full shape. The body is the artifact — don't compose it inline in a single bash call.

### 3. Run the PR creation

```bash
gh pr create --title "<type>(<scope>): <subject>" --body "$(cat <<'EOF'
[full body per the shape above]
EOF
)"
```

For draft PRs add `--draft`. For draft PRs with a `blocked:` reason, also run `gh pr edit <N> --add-label "blocked: <reason>"`.

### 4. After the codex-pr review (if code), mark ready and merge

```bash
gh pr ready <N>
gh pr merge <N> --squash --delete-branch
```

For PRs sitting in worktrees that block local branch deletion, that's a known wrinkle — the remote merge still succeeds, just clean the worktree after.

### 5. Confirm the issue auto-closed

`gh issue view <N>` — if not, comment-close manually with a pointer to the merged PR.

## Title and commit message conventions

Title format: `<type>(<scope>): <subject under 70 chars>`

Types in use in Ray's repos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`. Scope is optional but usually matches the area (`mentor`, `rubric`, `approaches`, `observability`).

Subject in imperative mood, no trailing period.

## When to invoke

- User says "open a PR", "ship this", "draft a PR", "send it through codex".
- User merges or closes a previous PR, freeing the deck for the next one.
- You finish a change in a worktree and the obvious next step is a PR.
- You are about to write `gh pr create` or `git commit -m`.

## Counter-cases (do NOT invoke)

- Filing a GitHub issue (use the issue-package mental model — different artifact).
- Drafting a research brief (use `research-brief` skill).
- Asking the user a decision (use `decision-package` skill).
- Committing locally with no intent to ship (a scratch commit) — still use the commit-message rules but not the PR-body shape.

## Output to the user after the PR is open

The chat message back to the user should include:
- The PR URL.
- A one-sentence summary of what's in it.
- The "things to push back on" surfaced as questions (verbatim from the body) so the user can answer in chat without opening the PR — the PR is the durable artifact, the chat is the fast lane.
- The next decision (merge, codex-pr review, voice pass, etc.).
