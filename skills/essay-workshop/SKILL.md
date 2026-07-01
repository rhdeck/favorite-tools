---
name: essay-workshop
description: Capture, workshop, and publish essays and mental models in Ray's State Change Notion workspace. Use this skill whenever Ray says anything like "save this as an essay," "this is an essay idea," "let's workshop this," "save this mental model," "that's a model worth keeping," "add this to the pipeline," "stash this for later," "this needs a name," or otherwise signals that something from the current conversation should be captured into his Essay Pipeline or Mental Models Workshop in Notion. Also trigger when Ray asks to extract essay ideas or mental models from a past chat, a Krisp transcript, or an email. Also trigger when Ray asks to advance an existing essay or model (move status, add image, mark mentor-ready). When in doubt, consult this skill before writing anything to Notion — the schema and conventions matter and shouldn't be guessed.
---

# Essay & Model Workshop

This skill manages Ray's essay and mental-model capture system in Notion. The workspace is "Essay & Model Workshop" inside his State Change team space.

## What's in the workspace

Two databases live under the **Essay & Model Workshop** page (`362d1752-4e0d-8141-92b7-ee76c4dae9ab`):

- **Essay Pipeline** — full lifecycle: Idea → Outline → Draft → Revised → Published → Repurposed
  - Database ID: `056f128b-6590-4811-8fdb-1f7326aee63b`
  - Data source ID: `30a35e32-e3a5-4cfb-a646-a238782947dd`
- **Mental Models Workshop** — Seed → Workshopping → Named → Productionized → Retired
  - Database ID: `3b9734f8-8cc9-4882-bba4-62cecebb1a9e`
  - Data source ID: `2380cea9-7f04-41eb-af26-3b047fe4003e`

These are the workshop. There is a separate, older **🧠 Mental Model Principles** database (data source `701fbe39-829d-4f26-8180-bae006675a5d`) which is the canonical gallery for fully-articulated, polished models. Don't write to it from this skill — productionized workshop entries graduate there by Ray's hand, not automatically.

## When to act vs. when to ask

**Act immediately (no confirmation) when:**
- Ray says "save this," "capture that," "add to the pipeline," or equivalent imperatives
- The thing to save is unambiguous (one idea, one model)

**Confirm first when:**
- The conversation contains multiple savable things and it's unclear which Ray wants
- The thing might be either an essay or a mental model (these often co-occur — see "Essay vs. model")
- Ray asks to extract from a past chat or transcript — propose the batch, get yes/no, then write

**Don't dump without permission.** Bulk extraction from chats should be proposed as a list first. Quality of the captured row matters more than completeness — a thin Idea row with a vague title pollutes the inbox.

## Essay vs. model — how to tell them apart

An **essay idea** is an argument with a thesis. It usually has a controlling metaphor or a specific case. Examples from Ray's existing work: "Stop Building Castles" (Clausewitz castle as ZIRP-era engineering), "Watch the Water, Not the Bucket" (operational vs. market attention), "Lab Coat in a Sales Meeting" (Robert Boulos positioning).

A **mental model** is a named conceptual move — a reusable way of seeing or deciding. It's the thing an essay might *use* to make its argument. Examples Ray has been working on: execution-speed discount, complementary cofounder trap, outside-advisor ceiling, narrative-product cohesion gap, psychic economy.

A useful test: if you can describe it as "the X trap" or "the Y move" or "the Z gap," it's probably a model. If it has a thesis and a case, it's probably an essay. The same insight often spawns both — a model gets named, and an essay applies it. Save both when both exist.

## Workflow for capturing a new essay idea

1. **Load the schema fresh** before writing. Don't trust memory for property names or option values; call `Notion:notion-fetch` on the data source (`collection://30a35e32-e3a5-4cfb-a646-a238782947dd`) and read the SQLite definition. Property names and options drift as Ray edits.
2. **Build the row.** Minimum fields for a new Idea:
   - `Name` — a working title (does not need to be the final title, but should be specific enough to find later; "AI thoughts" is not specific enough, "Why Atlassian's product surface is a tell" is)
   - `Status` — almost always `Idea` at capture time
   - `Source` — `Chat` if from a Claude conversation, `Meeting` if from a Krisp transcript, `Email` if from Gmail, `Conversation` for an in-person discussion, `Observation` if Ray just thought it up
   - `Source Link` — link back to the chat or document if one exists
   - `Captured` — today's date
   - `Tags` — pick the relevant ones from the existing set; don't invent new tags unless Ray explicitly asks
3. **Optional but valuable when available:**
   - `Controlling Metaphor` — if there's already a candidate metaphor, capture it. This is the single highest-value field for essays Ray will actually write.
   - Page body — a 2-5 sentence note on what the essay would argue and why it matters. Not a draft. Enough that future-Ray opening the row knows what past-Ray was thinking.
4. **Do not** fill in `Published`, `Published URL`, `Image`, `Image Prompt`, `Word Count Target`, or `Publication Target` at Idea stage. Those come later.
5. Use `Notion:notion-create-pages` with `data_source_id` parent `30a35e32-e3a5-4cfb-a646-a238782947dd`.

## Workflow for capturing a new mental model

1. **Load the schema** for `collection://2380cea9-7f04-41eb-af26-3b047fe4003e`.
2. **Build the row.** Minimum fields for a Seed:
   - `Name` — the candidate name. If the model has been named in conversation, use that name. If it's still nameless, use a descriptive placeholder in quotes: `"the trap where founders hire complementary cofounders too early"` — easier to find than `Cofounder issue`.
   - `Status` — `Seed` unless Ray has explicitly named or workshopped it further
   - `Captured` — today
   - `Origin` — short note on where it came from. Examples: `Xano strategic analysis, Dec 2025`, `Sutro call with Tomas Apr 11`, `State Change mastermind with Robert`.
3. **Valuable when available** — these are what make a model usable, not just stored:
   - `Definition` — one sentence. The compressed statement of the model.
   - `The Move` — what the model lets you *do* differently. The action it unlocks.
   - `Counter-Pattern` — what it warns against. The failure mode it names.
   - `Source Chats` — copy the chat URL or describe the source so the original argument can be retrieved.
   - Page body — examples, source quotes, the longer workshopping notes.
4. **Don't check `Mentor Ready`** until Ray explicitly says it's ready or until status reaches Productionized.
5. **`Related Essays`** — if there's a corresponding essay row, link it. The relation is two-way so the essay's page will surface this model automatically.

## Workflow for advancing an existing entry

When Ray says things like "move that essay to Draft," "mark that model as Named," or "this is ready for the mentor":

1. Search for the entry by name (use `Notion:notion-search` with the data source filter).
2. Use `Notion:notion-update-page` to change `Status`, set `Mentor Ready`, or add fields that weren't there at capture time.
3. When moving an essay to `Published`, also set `Published` date and `Published URL`.
4. When moving a model to `Productionized`, ask Ray whether to also create a polished version in the Mental Model Principles gallery. Don't do it without asking — the gallery has a different, richer schema and Ray may want to write that entry by hand.

## Extracting from a past chat or transcript

When Ray asks to mine a past conversation for essay ideas or models:

1. Search past chats with `conversation_search` if it's a Claude chat, or `Krisp:search_meeting_content` if it's a meeting.
2. **Propose first, write second.** Return a numbered list: "Here's what I'd pull — 3 essay ideas and 2 models. Want me to add all five, or just some?"
3. For each proposed entry, include: the candidate name, which database it goes in, and a one-line "why this is worth capturing." This makes it easy for Ray to veto thin ones.
4. After Ray confirms, write them in. Use the Source Link field to point back to the chat or transcript so the trail is preserved.

## Tag discipline

The Tags multi-select on both databases shares a vocabulary. Use these and only these unless Ray explicitly asks for a new one:

`AI`, `Strategy`, `Economics`, `Xano`, `AI Transition`, `Software`, `Psychic Economy`, `Mental Models` (essay-only — marks essays whose subject is a model), `Investing`, `Operations`, `Founders` (model-only).

When uncertain between two tags, pick the more specific one. `Xano` over `Strategy` for a Xano-specific piece. `Psychic Economy` over `Founders` for psychic-economy-specific content.

## What not to do

- Don't write to **Essay Drafts 2026** or the old **Essays** database under Charlotte. Those are the legacy Weekly Letters workflow and live in a different part of Notion. The new pipeline is the workshop.
- Don't write to **Mental Model Principles** unless Ray explicitly asks. That's the gallery, not the bench.
- Don't invent new Status values, new Source options, or new Tag options. If a row genuinely needs an option that doesn't exist, surface it: "This doesn't fit any existing tag — want me to propose adding one?"
- Don't fill in `Image`, `Image Prompt`, or `Image Style` at Idea capture. Image work happens at Draft stage or later.
- Don't auto-link essays to models or models to essays unless the connection is explicit in the conversation. Speculative cross-linking pollutes the graph.

## Best practices (extracted from working sessions)

See `references/best-practices.md` for the accumulated playbook — what makes a good Idea row, what makes a good Seed model, common pitfalls, and patterns Ray has reinforced. Read it before any bulk extraction pass.

## Voice and writing

When drafting essay content in the page body (outline notes, draft prose), match Ray's voice. The `ray-voice` skill covers the patterns: short declarative sentences, no em-dashes, no hedging, controlling metaphor as architecture, callbacks, plain muscular verbs. If you're writing more than 3-4 sentences of essay-body content, read the `ray-voice` skill first.

## Quick reference — IDs

| Thing | ID |
|---|---|
| Essay & Model Workshop page | `362d1752-4e0d-8141-92b7-ee76c4dae9ab` |
| Essay Pipeline database | `056f128b-6590-4811-8fdb-1f7326aee63b` |
| Essay Pipeline data source | `30a35e32-e3a5-4cfb-a646-a238782947dd` |
| Mental Models Workshop database | `3b9734f8-8cc9-4882-bba4-62cecebb1a9e` |
| Mental Models Workshop data source | `2380cea9-7f04-41eb-af26-3b047fe4003e` |
| Mental Model Principles (gallery, read-only here) | `701fbe39-829d-4f26-8180-bae006675a5d` |
