# operating-model

The operating system for the graveyard way of working. (This repo was renamed from `favorite-tools`.)

Built and maintained at [State Change AI](https://statechange.ai), where we work on this kind of thing.

## Operating model

This is not a tool bag — it is the operating model for building big things with autonomous graveyard shifts. The thesis: work compounds only when knowledge is externalized into substrates that are **versioned, visible, and cold-resumable** (git and Notion), never trapped in a chat transcript or a local memory file. Every fact has exactly one home, sorted by scope (this project vs. how-we-operate) and kind (transient work vs. durable knowledge); a project earns its way from live-in-chat inception to a self-describing, externally-driven graveyard phase through a deliberate externalization event. The human-readable constitution lives in `docs/`; the skills below are the executable canon that runs it.

- [`docs/operating-model.md`](docs/operating-model.md) — the constitution: thesis, the two-axis/four-homes grid, and the versioned-visible-cold-resumable rule.
- [`docs/lifecycle.md`](docs/lifecycle.md) — the three-phase lifecycle and why the externalization event is the whole game.
- [`docs/knowledge-homes.md`](docs/knowledge-homes.md) — the four homes in depth, the repo contract, and the local-memory anti-pattern.
- [`docs/coordination.md`](docs/coordination.md) — inter-project coordination: each project is an autonomous division, and the only sanctioned way for one to affect another is to inject a GitHub issue into its repo (issues are also the cross-project message bus); loops become async issue-injection.

## Skills

| Skill | Description |
| --- | --- |
| [`graveyard-shift`](skills/graveyard-shift) | Work through the open issue backlog autonomously. Auto-ship the small clean fixes, prep draft PRs for review on bigger ones, and file refined proposals when design choices need user input — for unattended sessions. |
| [`setup-graveyard-project`](skills/setup-graveyard-project) | Make a project graveyard-ready: perform the externalization event — backlog → issues, technical canon → repo docs + CLAUDE.md, strategic state → a Notion Project Overview — so any cold agent can resume from git + Notion alone. |
| [`observation-mode`](skills/observation-mode) | Ship judgment-shaped work into a watched window instead of blocking on pre-merge certainty: reopen with an `observing` label and an instrumented Signal source (artifact + query + threshold), then graduate or fold-into-fix on the reading. |
| [`credit-pacing`](skills/credit-pacing) | Check AI credit/budget before a costly spend and pace around a tapped window — turn "pause" into "gate that one path, keep working," and turn overage into a scheduled wait for the reset. The budget discipline a graveyard shift runs on. |
| [`codex-pr`](skills/codex-pr) | Create a PR, review with `codex review`, fix issues in a loop until clean, then auto-merge. |
| [`pr-package`](skills/pr-package) | Open a pull request as a decision package — summary, inline content to review, explicit "things to push back on," a checkbox test plan, and `Closes #N` — so the user reviews once with every load-bearing call surfaced. |
| [`shape-an-epic`](skills/shape-an-epic) | Turn an underspecified "epic" issue into a concrete proposal comment — recommendation, sketch, phase plan, and trigger criteria — using a Shape Up pitch adapted for GitHub issues. |
| [`research-brief`](skills/research-brief) | Produce a research, survey, or analysis document as a skimmable markdown brief with a generated infographic prepended at the top. |
| [`notion-briefs`](skills/notion-briefs) | Set up (or repair) the cross-project Notion "Briefs" system in a new environment — install the publisher CLI, attach to a Notion page, and create one shared, newest-first database every project can publish briefs and shift reports to. |
| [`interoffice-memo`](skills/interoffice-memo) | Send or handle a cross-division "interoffice memo" — a request from one project to another on the GitHub-issues message bus (labeled `interoffice-memo`). Covers both ends: inject a want into another repo, or adjudicate one your shift receives. Enacts `docs/coordination.md`. |
| [`essay-workshop`](skills/essay-workshop) | Capture, workshop, and publish essays and mental models through the State Change Notion pipeline. The content counterpart to `notion-briefs`: how the operating model manages the content pipeline the way the rest manages code. |
| [`avoid-ai-voice`](skills/avoid-ai-voice) | Strip the tells of generic AI writing — slop cadence, hollow hedging, reflexive symmetry — so published prose doesn't read as machine-generated. The voice guardrail on the content pipeline. |

## Installing a skill

Each skill lives in its own directory under [`skills/`](skills) with a `SKILL.md`. To use one, copy its directory into your Claude skills directory:

```sh
# User-level (available everywhere)
cp -R skills/graveyard-shift ~/.claude/skills/

# Or project-level
cp -R skills/graveyard-shift .claude/skills/
```

## License

[MIT](LICENSE) © Ray Deck / [State Change AI](https://statechange.ai)
