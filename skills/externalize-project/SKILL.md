---
name: externalize-project
description: Perform the externalization ceremony that declares a project graveyard-managed — sweep everything in heads and chat into durable substrate (GitHub issues, repo docs, Notion Project Overview) so any cold agent can resume from git + Notion alone. Use when the user says "externalize this project", "make this graveyard-ready", "declare this graveyard-managed", "set up the graveyard contract", or when a project is about to flip from live/inception work into the autonomous graveyard phase.
---

# Externalize a Project

This is the **externalization event** — the deliberate ceremony that flips a project into the graveyard phase. Its single job: get every piece of load-bearing knowledge **out of heads and transcripts and into durable substrate**, so a cold agent who has never seen the conversation can pick the project up tomorrow with nothing but `git clone` + the Notion Project Overview.

Externalization is **step 2 of the graveyard way of working, and it is the whole game.** A graveyard shift (the autonomous backlog drain) is only lossless if the handoff substrate is real. If knowledge is still trapped in a chat transcript or a local agent-memory file, the next cold agent starts blind and the model collapses. This skill is what makes "clear the session and resume from disk" a true statement.

This skill *implements* the conceptual canon in `docs/operating-model.md` (the four homes for knowledge) and `docs/lifecycle.md` (the phase transitions). Read those first if they exist — this skill is the executable form of those documents. (They may live in a sibling PR and not be on `main` yet; reference them by relative path regardless.)

## The principle: four homes, nothing in two

Every piece of knowledge has exactly **one** durable home. Externalization is the act of routing each piece to its home and deleting the copies that were living somewhere temporary.

| Knowledge | Its one durable home |
|---|---|
| Project work to be done | GitHub issues / PRs |
| Global work to be done | Notion Briefs DB |
| Project durable knowledge (technical) | Repo docs (`CLAUDE.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`) |
| Project durable knowledge (strategic) | Notion Project Overview |
| Global durable knowledge | Skills + global `CLAUDE.md` |

The two **project** homes must never duplicate each other, because they serve different readers:

- **Repo docs = the technical canon an AGENT reads to execute.** What the system is, why it's built this way, how to work in it. Lives in git so it versions with the code and a cold agent reads it on `clone`.
- **Notion Project Overview = the strategic state a HUMAN reads to re-orient.** What this project is, what phase it's in, where the work lives. The Overview **points to git — it never copies it.** Status, links, a one-line purpose, the last-externalized date. If you find yourself pasting architecture into the Overview, stop: that belongs in `docs/ARCHITECTURE.md`, and the Overview should link to it.

When in doubt about where something goes: *would an agent need this to execute?* → repo docs. *Would a human need this to decide whether to re-engage?* → Overview. *Is it a unit of work?* → an issue. If it's none of those, it probably isn't load-bearing and can be dropped.

## The minimal graveyard-ready repo contract

A repo cannot flip to the graveyard phase until **all four** of these exist. This is the contract the ceremony is driving toward — the checklist below is just the work of satisfying it:

- **`CLAUDE.md`** — agent operating instructions / the technical-canon entry point. The first thing a cold agent reads.
- **`docs/OVERVIEW.md`** — one-line purpose + a LINK to the Notion Project Overview. Points out; never duplicates strategic state.
- **`docs/DECISIONS.md`** — the decision log. Why things are the way they are.
- **`docs/ARCHITECTURE.md`** — architecture canon. What the system is and how it fits together.

If any of the four is missing at the end, the project is **not** graveyard-ready and you must not report it as such.

## The ceremony

Drive the project through these seven steps in order. Earlier steps surface knowledge; later steps route it home and verify nothing leaked.

### 1. Issue hygiene — sweep heads and chat into GitHub issues

Everything that is a *unit of work* must become a GitHub issue. Walk the recent conversation, any local TODO/notes files, scratchpad memory, and the user's stated intentions, and file what isn't filed.

- `gh issue list --state open` to see what already exists; don't duplicate.
- For each piece of pending work still living in chat or someone's head, open an issue with a real problem statement — enough that a cold agent could pick it up. A one-line "fix the thing" issue is not externalized knowledge; it's a reminder to re-derive it later.
- Triage: apply labels/priority so the backlog is *real and ordered*, not a pile. A graveyard shift will consume this list directly, so the ordering you leave is the ordering it executes.
- This is the moment to be honest about scope. Work the user mentioned but never filed will be **lost** the instant the transcript is cleared. If it matters, it's an issue now.

### 2. Seed the technical canon — `docs/DECISIONS.md` and `docs/ARCHITECTURE.md`

Create `docs/` if needed. These two files are the durable answer to "why is it like this" and "what is it."

- **`docs/DECISIONS.md`** — a running decision log, newest-first or dated entries. Capture the load-bearing calls made so far: the ones currently living only in the conversation ("we decided to use X over Y because Z"). Each entry: the decision, the date, and the *why* — the why is the part that's expensive to reconstruct and the part that rots fastest in memory. A future agent reads this to avoid re-litigating settled calls.
- **`docs/ARCHITECTURE.md`** — what the system is: components, data flow, where things live, the key boundaries. Enough that an agent can navigate the codebase without spelunking. Point to real paths. Don't transcribe every file; capture the shape and the load-bearing constraints.

Write what's *true now*, sourced from the conversation and the code — not aspirations. An aspiration is an issue (step 1), not architecture.

### 3. Write `CLAUDE.md` — the agent operating instructions

This is the entry point a cold agent reads first. It is the technical-canon index plus the rules of the road for working in *this* repo:

- One-paragraph statement of what the project is and its current phase (graveyard).
- Pointers into the canon: "decisions live in `docs/DECISIONS.md`, architecture in `docs/ARCHITECTURE.md`, strategic state in the Notion Overview linked from `docs/OVERVIEW.md`."
- Project-specific operating rules: how to build/test/run, conventions, guardrails, anything an agent must know before touching code.
- Keep it an *index and a ruleset*, not a duplicate of the canon — it points to DECISIONS/ARCHITECTURE, it doesn't restate them.

### 4. Create the Notion Project Overview (strategic state)

Create the project's page in the Notion Project Overviews database via the briefs publisher CLI at `~/.config/ai-briefs/notion_briefs.py`. (If the briefs system isn't configured in this environment — no `~/.config/ai-briefs/token` — run the `notion-briefs` setup skill first.)

The Overview page holds: **Name · Status · Repo (URL) · One-line purpose · Last externalized (date) · Body.** The body is strategic orientation for a *human*: what this project is for, what phase it's in, where the live work is — with **links** to the repo, the issues, and the docs. It does not copy architecture or decisions; it points at them.

- Set **Status → Graveyard**.
- Stamp **Last externalized** with today's date.
- Confirm the **Repo URL** and **one-line purpose** are present.

Check the publisher's `README.md` in `~/.config/ai-briefs/` for the exact command/flags, since the Overviews database and its schema are managed there. If a Project Overview page already exists for this repo, **update it** (status, last-externalized, body) rather than creating a duplicate.

### 5. Drop the `docs/OVERVIEW.md` stub

A thin file — a few lines — that exists so an agent in the repo can find the strategic state without leaving git:

- The one-line purpose.
- A link to the Notion Project Overview page (the URL from step 4).
- One sentence saying strategic/current state lives in the Overview; this file just points there.

That's it. If `docs/OVERVIEW.md` grows past a short stub, knowledge has leaked back in — it's a pointer, not a home.

### 6. Integrity check — no load-bearing knowledge left behind

This is the step that makes externalization *honest*, and it's the one most likely to be skipped. Verify that nothing load-bearing now lives **only** in a transcript or a local memory file.

- Re-read the recent conversation with one question: *if this chat were deleted right now, what would be lost?* Anything that surfaces is a leak — route it: a decision → `docs/DECISIONS.md`, an architectural fact → `docs/ARCHITECTURE.md`, a unit of work → an issue, strategic context → the Overview.
- Inspect any local agent-memory files (`.memory`, scratchpad notes, agent state, CLAUDE.local.md, etc.). **Local memory is demoted to a thin accelerant — ideally ~zero — never a source of truth.** Anything in it that's load-bearing gets externalized to its real home, then the local copy is cleared or reduced to a stub that just points at the durable homes.
- The test for success: *could a cold agent who has only `git clone` + the Notion Overview, and has never seen this conversation, resume this project?* If the answer is "no, they'd be missing X," then X hasn't been externalized — go put it home.

### 7. Confirm the contract → graveyard-ready

Verify all four contract files exist and are non-stub (except OVERVIEW.md, which is *supposed* to be a stub):

```bash
ls CLAUDE.md docs/OVERVIEW.md docs/DECISIONS.md docs/ARCHITECTURE.md
```

Confirm the Notion Overview shows Status = Graveyard with today's last-externalized date. Only when both the repo contract and the Overview are satisfied is the project graveyard-ready. Report it as ready — and only then.

## Anti-patterns

- **Duplicating the canon into the Overview.** The Overview points to git; it never copies architecture or decisions. Strategic state for humans, not technical canon for agents.
- **Stub issues.** "Fix the parser" is not externalized work — it's a note to re-derive the work later. Externalize the *problem statement*, not just the title.
- **Skipping the integrity check.** The whole point is honesty about what's left in the transcript. A ceremony that creates four files but leaves the real reasoning in chat has externalized nothing.
- **Keeping local memory as a source of truth.** Local agent memory is a thin accelerant at most. If clearing it would lose something, it wasn't externalized.
- **Aspirations in the canon.** `docs/ARCHITECTURE.md` describes what *is*; future plans are issues. Don't write the canon as a wish list.
- **Declaring graveyard-ready with the contract incomplete.** All four files plus the Overview, or it's not ready. No partial credit.

## When NOT to use this skill

- The project is still in active live-with-the-user design — externalize when the thinking has *settled* enough to be durable, not mid-deliberation.
- You only need to publish a one-off brief or shift report — that's the briefs CLI / `graveyard-shift`, not a full externalization.
- The project is already graveyard-managed and you're just doing a shift — use `graveyard-shift`. Re-run *this* skill only to re-externalize after a substantive live session has accumulated new durable knowledge (then re-stamp Last externalized).
