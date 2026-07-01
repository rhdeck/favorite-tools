---
name: notion-briefs
description: Set up (or repair) the cross-project Notion "Briefs" system in a new environment — install the publisher CLI globally, solicit a Notion integration key, attach to a user-chosen Notion page, create an inline Briefs database, and register the tool in the global CLAUDE.md so every project can publish briefs/shift reports to one shared, newest-first database. Use when the user says "set up Notion briefs," "install the briefs tool here," "I need briefs in this environment," or when a brief publish fails because nothing is configured.
metadata:
  version: 1.0.0
---

# Notion Briefs — setup

This skill installs a **cross-project brief/shift-report publisher** backed by a single Notion database, and wires it into the environment so any project's agent can use it. It is **portable**: run it once per machine/environment the user works in. The end state mirrors the reference setup — an inline "Briefs" table living on a Notion page the user owns, fed by a project-neutral CLI.

The CLI and a README ship **inside this skill** (`notion_briefs.py`, `README.md`) — they are the source of truth; the install step copies them out to a global location.

## What you will end up with

- `~/.config/ai-briefs/notion_briefs.py` — the publisher (stdlib only, no pip deps)
- `~/.config/ai-briefs/token` — the Notion integration secret (`chmod 600`)
- `~/.config/ai-briefs/config.json` — `{"briefs_db": "<id>"}`, written by bootstrap
- A **"Briefs" inline database** on a Notion page the user picks (props: Name, Date, Project, Type, Status)
- A pointer block in the global `~/.claude/CLAUDE.md` so every project discovers the tool

## Idempotency — check before you act

Before doing anything, check what already exists and only fill gaps:

```bash
ls -la ~/.config/ai-briefs/ 2>/dev/null
cat ~/.config/ai-briefs/config.json 2>/dev/null   # has briefs_db? → DB already bootstrapped
test -s ~/.config/ai-briefs/token && echo "token present" || echo "need token"
grep -q "ai-briefs/notion_briefs.py" ~/.claude/CLAUDE.md && echo "CLAUDE.md pointer present" || echo "need CLAUDE.md pointer"
```

If everything is present and `notion_briefs.py list` works, there's nothing to do — report that and stop. Otherwise do only the missing steps.

## Step 1 — Install the CLI globally

Copy the bundled files out of the skill to the global config dir (this dir is intentionally **not** tied to any repo, so every project shares it):

```bash
mkdir -p ~/.config/ai-briefs
cp "<skill-dir>/notion_briefs.py" ~/.config/ai-briefs/notion_briefs.py
cp "<skill-dir>/README.md"        ~/.config/ai-briefs/README.md
chmod +x ~/.config/ai-briefs/notion_briefs.py
```

(`<skill-dir>` is this skill's own directory — the same folder this `SKILL.md` lives in.)

## Step 2 — Get a Notion integration key (solicit from the user)

Talking to Notion's API requires an **internal integration** (a Notion "application") and its secret token. If `~/.config/ai-briefs/token` is missing or empty, walk the user through creating one — **do not invent or guess a key**:

> To let me publish into Notion, I need an integration key. Please:
> 1. Go to **https://www.notion.so/my-integrations** → **New integration**.
> 2. Pick **Internal** integration, name it (e.g. "AI Briefs"), select your workspace, and submit.
> 3. Copy the **Internal Integration Secret** (starts with `ntn_…` or `secret_…`) and paste it here.

When the user provides it, write it to a file (never leave it only in chat; tell them they can rotate it later):

```bash
umask 077
printf '%s' '<PASTED_SECRET>' > ~/.config/ai-briefs/token
chmod 600 ~/.config/ai-briefs/token
```

Validate it before continuing:

```bash
curl -s https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer $(cat ~/.config/ai-briefs/token)" \
  -H "Notion-Version: 2022-06-28" | head -c 300
```

A valid key returns a `bot` user object; an error means the key is wrong — re-solicit.

## Step 3 — Solicit the target page URL (different per environment — NEVER assume)

**The page is environment/client-specific. Do not reuse a UUID from another setup or hardcode the reference workspace's page.** Always ask the user for the URL of the page *in this workspace* that the Briefs table should live on.

> Where should the Briefs table live? In Notion:
> 1. Create (or pick) a page **you own** — e.g. call it "AI Briefs".
> 2. Open it → **•••** (top-right) → **Connections** → add your integration (the one whose key you gave me). **This is mandatory** — Notion only lets an integration see pages explicitly connected to it, and it cannot be scripted.
> 3. Copy the page URL (Share → Copy link) and paste it here.

Verify the integration can actually see that page before bootstrapping (catches the "forgot to connect" case):

```bash
PAGE_ID=$(python3 -c "import re,sys;print(re.search(r'[0-9a-fA-F]{32}', sys.argv[1].replace('-','')).group())" '<PASTED_PAGE_URL>')
curl -s "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $(cat ~/.config/ai-briefs/token)" \
  -H "Notion-Version: 2022-06-28" | head -c 300
```

If it returns `object_not_found`, the integration isn't connected to the page yet — ask the user to do the Connections step, then retry. Do not proceed past this gate.

## Step 4 — Bootstrap the inline database

```bash
python3 ~/.config/ai-briefs/notion_briefs.py bootstrap --parent '<PASTED_PAGE_URL>'
```

This creates the "Briefs" database **inline** (a live table on the page), saves its id to `config.json`, and prints the database URL. Properties: **Name · Date · Project · Type** (Shift Report / Brief / Plan) **· Status** (Active / Superseded / Collected — the brief lifecycle, see README). New Project/Type/Status names auto-register on write, so new projects need no schema change.

Tell the user two UI-only tweaks they may want (the API can't set view sort/filter): set the table's default **Sort → Date, Descending** so newest floats to top, and add per-project filtered views as they accumulate.

## Step 5 — Register the tool in the global CLAUDE.md

So every project's agent discovers the tool without being told, ensure `~/.claude/CLAUDE.md` contains a pointer. If the `grep` in the idempotency check showed it missing, append this section:

```markdown
## Briefs & shift reports go to Notion (cross-project)

Briefs, shift reports, and plans for **any** project publish to one shared Notion "Briefs" database via the project-neutral CLI at **`~/.config/ai-briefs/notion_briefs.py`** (see that dir's `README.md`). One database, newest-first, tagged by `--project`; new project names auto-register, so this works the same from every repo without per-project setup. Prefer this over leaving a local `test-plans/*.md` brief. Publish at the end of a graveyard shift or a substantive session, then hand me the page URL — that page becomes where we iterate on the brief. The token lives in `~/.config/ai-briefs/token` (never paste it in chat). **If the tool isn't configured here** (no token / no `config.json`), run the **notion-briefs** setup skill — solicit a Notion integration key and the target page URL first.
```

## Step 6 — Verify end-to-end

Prove the chain before declaring done — don't hand back an unverified setup:

```bash
# publish a tiny smoke-test brief, then confirm it lists, then optionally delete it in the UI
printf '# Setup smoke test\n\nNotion Briefs configured in this environment.\n' > /tmp/brief-smoke.md
python3 ~/.config/ai-briefs/notion_briefs.py publish \
  --project "Setup" --date "$(date +%F)" --title "Setup smoke test" \
  --type Brief --status Active --file /tmp/brief-smoke.md
python3 ~/.config/ai-briefs/notion_briefs.py list
```

Hand the user the database/page URL and tell them the smoke-test row is safe to delete. If `date` isn't desirable, pass an explicit `--date YYYY-MM-DD`.

## Daily use (after setup)

```bash
python3 ~/.config/ai-briefs/notion_briefs.py projects        # check the project pick-list first
python3 ~/.config/ai-briefs/notion_briefs.py publish \
  --project "<Project>" --date YYYY-MM-DD --title "Shift Report YYYY-MM-DD" \
  --type "Shift Report" --status Active --file report.md      # prints the page URL
python3 ~/.config/ai-briefs/notion_briefs.py list [--project "<Project>"] [--status Active]   # newest-first
python3 ~/.config/ai-briefs/notion_briefs.py append <url> --file closeout.md --divider        # "what we did" footer
python3 ~/.config/ai-briefs/notion_briefs.py set-status <url> --status Collected               # off Active
```

The brief is a living lifecycle object (**Active → Superseded | Collected**). Mark the prior report **Superseded** when a newer one rolls its open items forward; mark a fully-worked brief **Collected** after appending its closeout footer. The graveyard-shift skill publishes + supersedes; the shift-change skill closes out (Collected). Full lifecycle in `README.md`.

### GitHub auto-linking (publish + append)

Bare issue/PR refs like `#308` in the markdown are **auto-linked to GitHub** so the user can click the number straight into the issue/PR — no manual linking needed. The repo is auto-detected from the **cwd's git remote** (so just run the publish from inside the project repo); override with `--github-repo owner/repo` if publishing from elsewhere. GitHub's `/issues/<n>` URL redirects to `/pull/<n>` for PRs, so issues and PRs both link correctly without distinguishing them. Refs inside `` `backticks` `` are left alone, and explicit `[text](url)` markdown links render as clickable links too. Write reports with plain `#NNN` — the tooling handles the linking.

## Project Overviews are paired with per-repo fill-issues

The publisher also backs a **Project Overviews** database (one page per project, `overview upsert` — see the CLI `README.md`). Seeding an overview page for a project is **atomic with injecting that project's fill-issue** (labeled `graveyard-infra`) into its repo — creating one without the other manufactures an orphan (an unfilled page that can never self-fill, or an issue with no page). The atomicity rule, the canonical fill-issue template, and the orphan-audit procedure live in the **`setup-graveyard-project`** skill; this note just points there.

## Notes / gotchas

- **Internal integrations cannot create workspace-level/root pages** — the database must nest under an existing page the user shared with the integration (Step 3). That's why we solicit a page URL instead of making one.
- **The Connections step (Step 3.2) is the one thing that can't be scripted.** Most setup failures are a forgotten connection — the page verify in Step 3 catches it.
- **Token hygiene:** the secret lives only in `~/.config/ai-briefs/token` (chmod 600). If it ever leaks into a transcript, the user can rotate it at notion.so/my-integrations and overwrite the file.
- The CLI is stdlib-only (urllib + json) and honors a `NOTION_TOKEN` env override if set, else the token file.
