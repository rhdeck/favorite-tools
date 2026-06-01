# favorite-tools

A collection of redistributable [Claude Code](https://claude.com/claude-code) skills.

Built and maintained at [State Change AI](https://statechange.ai), where we work on this kind of thing.

## Skills

| Skill | Description |
| --- | --- |
| [`graveyard-shift`](skills/graveyard-shift) | Work through the open issue backlog autonomously. Auto-ship the small clean fixes, prep draft PRs for review on bigger ones, and file refined proposals when design choices need user input — for unattended sessions. |
| [`codex-pr`](skills/codex-pr) | Create a PR, review with `codex review`, fix issues in a loop until clean, then auto-merge. |
| [`research-brief`](skills/research-brief) | Produce a research, survey, or analysis document as a skimmable markdown brief with a generated infographic prepended at the top. |

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
