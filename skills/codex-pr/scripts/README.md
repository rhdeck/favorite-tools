# Budget-aware review scripts (bundled with codex-pr)

These ship with the skill so the review mechanism travels with it.

| script | what it does |
|---|---|
| `review [base]` | Runs one review pass against `base` (default `main`). Picks the engine by budget, prints findings tagged `[P1]/[P2]/[P3]`. Evaluates three dimensions: code correctness, **issue fidelity** (does it solve the issue?), and **documentation fidelity & drift** — the latter two via a rubric fed to either engine. Feeds the engine the diff (`git diff base...HEAD`) on stdin + the rubric prompt: codex via `codex exec -s read-only`, agy via `agy -p`. (Not `codex review --base <BRANCH> <PROMPT>` — codex-cli 0.133+ made those args mutually exclusive, which would silently drop the rubric.) |
| `pick-review-engine` | Prints `codex` or `agy` based on remaining Codex quota. `review` calls this. |
| `budget` | Prints remaining Codex/Claude quota across windows. |
| `install.sh` | Symlinks the above onto your PATH (default `~/.local/bin`) for interactive use. |

## Prerequisites
- **`codex`** CLI (primary engine) and/or **`agy`** CLI (Antigravity/Gemini, fallback). At least one must be installed.
- **CodexBar** (`com.steipete.codexbar`, macOS) for live budget data. *Optional* — without it the scripts can't see budget and fall back to the default engine (codex, or `REVIEW_DEFAULT_ENGINE`).

## Env knobs
- `REVIEW_ENGINE=codex|agy` — force an engine for a run.
- `REVIEW_BUDGET_THRESHOLD=98` — percent at which a Codex window counts as tapped.
- `REVIEW_DEFAULT_ENGINE` — engine to use when there's no budget data.
- `CODEXBAR_HISTORY` — override the CodexBar cache directory.
- `REVIEW_CONTEXT_FILE` — path to a file with the issue body + PR description. When set, `review` feeds it to the engine so it can judge whether the change actually solves the issue. Without it, the issue-fidelity check degrades to "intent unverifiable" and the other two dimensions still run.

## Install
```sh
bash install.sh            # symlinks into ~/.local/bin
```

The `codex-pr` skill calls `review` directly from this directory, so installation
is only needed for running them yourself in a terminal.
