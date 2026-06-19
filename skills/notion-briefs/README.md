# AI Briefs — cross-project brief/report publisher

A **single Notion database** ("Briefs") that holds AI-generated briefs, shift
reports, and plans across **all** of Ray's projects and initiatives — newest
first, tagged by project. This directory is intentionally project-neutral
(`~/.config/ai-briefs/`), so any project's agent can publish into the same place
and hand Ray a URL.

## Files here

- `notion_briefs.py` — the CLI (stdlib only; no pip deps).
- `token` — Notion integration secret, `chmod 600`. Never commit/paste; rotate in
  Notion → My integrations if it leaks.
- `config.json` — `{"briefs_db": "<database_id>"}`, written by `bootstrap`.

## One-time setup

1. Create a Notion page Ray owns (e.g. "AI Briefs"), then **connect the
   integration to it**: page → ••• → Connections → add the integration. Notion
   only exposes pages explicitly connected to an integration — this step is
   mandatory and cannot be scripted.
2. `python3 notion_briefs.py bootstrap --parent <ai-briefs-page-url>`
   Creates the "Briefs" database (props: Name, Date, Project, Type, Status) and
   saves its id to `config.json`.

## Publishing a brief (any project)

```bash
python3 ~/.config/ai-briefs/notion_briefs.py publish \
  --project "Smart Terminal" \
  --date 2026-06-18 \
  --title "Shift Report 2026-06-18" \
  --type "Shift Report" \        # Shift Report | Brief | Plan (auto-grows)
  --status Active \              # Active | Superseded | Collected
  --file path/to/report.md
```

Markdown is converted to Notion blocks (headings, bullets, numbered lists,
quotes, code fences, tables→bullets, dividers, **bold**, `code`). New Project /
Type / Status option names auto-register, so a brand-new project just works — no
schema edit.

**Check the project pick-list before publishing.** Run `projects` and match the
existing option name exactly — `publish` auto-registers whatever string you pass,
so a typo (`smart-terminal` vs `Smart Terminal`) silently creates a *second*
project and splits the history. If the current project genuinely isn't in the
list yet, publishing with its name is what adds it.

```bash
python3 ~/.config/ai-briefs/notion_briefs.py projects        # current Project options
```

## Brief lifecycle (Status)

A brief is a living object you have a conversation with, not a write-once log:

- **Active** — open and in front of the user. Exactly one Active report per
  project at a time (the canonical current state).
- **Superseded** — a newer report of the same kind rolled forward and replaced it;
  its still-open items were carried into the new Active one.
- **Collected** — worked all the way through and closed out: the decisions were
  resolved/acted on and a "what we did" footer was appended. Nothing left open.

When you finish working a brief, **append the closeout footer, then flip it off
Active** — that's what lets you move to the next one:

```bash
# add a "## What we did" footer to the bottom of an existing brief
python3 ~/.config/ai-briefs/notion_briefs.py append <page-url-or-id> --file closeout.md --divider

# flip its lifecycle status
python3 ~/.config/ai-briefs/notion_briefs.py set-status <page-url-or-id> --status Collected
```

(`<page-url-or-id>` accepts a full Notion URL or a bare 32-char id.)

## Listing

```bash
python3 ~/.config/ai-briefs/notion_briefs.py list                       # all, newest first (shows Status)
python3 ~/.config/ai-briefs/notion_briefs.py list --project "Smart Terminal"
python3 ~/.config/ai-briefs/notion_briefs.py list --status Active       # what's still open
python3 ~/.config/ai-briefs/notion_briefs.py list --project "Smart Terminal" --status Active --type "Shift Report"
```

The last form is how you find the prior Active report to supersede / diff against.

## How agents should use this

- **End of a graveyard shift or a substantive session:** publish the brief here
  instead of leaving a local `test-plans/*.md` file. The newest Active row for a
  project is its canonical current state; carry unresolved items forward into the
  next brief, then supersede the old one. (The graveyard-shift skill points here.)
- **Working a brief live (shift change):** when its items are resolved, append the
  closeout footer and mark it Collected before moving on. (The shift-change skill
  points here.)
- The token env override `NOTION_TOKEN` is honored if set, else the `token` file.
