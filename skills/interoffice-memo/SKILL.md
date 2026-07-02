---
name: interoffice-memo
description: Send or handle a cross-division "interoffice memo" — a request from one project (line of business) to another, carried on the GitHub-issues message bus. Use when you need to ask another project to do or consider something (you are NOT allowed to edit its repo yourself), when your shift encounters an issue labeled `interoffice-memo` (another division is asking YOU for something), or when the user says "send a memo to <project>", "coordinate with <project>", "ask <project> to...". Enacts the inter-project coordination protocol in docs/coordination.md.
---

# Interoffice Memo

The way two autonomous divisions talk. Each project/repo is a **vice president of its own division** — it owns its tree and adjudicates its own backlog. When one division needs something from another, it does **not** reach in and do the work; it sends an **interoffice memo**: a GitHub issue injected into the target's repo, labeled `interoffice-memo`. The issue *is* the message. The requester supplies a **want**; the target's orchestrator decides **how** — or **whether** — to act, on its own shift.

This skill is the operational how-to for both ends of that memo. The *why* lives in [`docs/coordination.md`](../../docs/coordination.md) (the coordination constitution) and the decision log; this skill enacts it. Read them if the rationale isn't obvious.

## The label is the protocol marker

Every interoffice memo carries the **`interoffice-memo`** label on the target repo. That label means one specific thing: *this issue is a request from another division, not a backlog item this repo authored for itself.* It is what lets any shift tell "my own work" from "another division's ask," and what makes memos queryable across repos (`gh issue list --label interoffice-memo`). Create the label in the target repo if it doesn't exist yet:

```bash
gh label create "interoffice-memo" --repo <target-owner>/<target-repo> --color 0e8a16 \
  --description "Cross-division request injected from another project (coordination bus)" --force
```

## Sending a memo

You are one division; you want something from another. Never edit their repo — send the memo.

1. **Discover the target.** There is no hardcoded roster. Find the division and its address in the Notion **Project Overviews** (the org chart — the target repo is the Overview's Repo field) and skim its recent **Briefs** (the status wire — is it active, what's its current state):
   ```bash
   python3 ~/.config/ai-briefs/notion_briefs.py overview list
   ```
   If the target has **no repo on its Overview**, you cannot route to it — that's a blocker to surface, not to work around. (See the routing-failure note in `docs/coordination.md`.)

2. **Write the memo as a *want*, not a spec.** Respect the division boundary: you supply intent and context; they decide the design. A good memo has:
   - **A "from" header** naming your division and repo, and a one-line statement that this is a sanctioned cross-division request (link `docs/coordination.md`).
   - **The want** — what you need, in outcome terms, not an implementation you're dictating.
   - **Context / constraints they should weigh** — anything from your canon or situation that bounds a good answer (this is what keeps them from solving the wrong problem).
   - **The ask** — explicit: "give this thought / shape it on your side — you own the decision."
   - **The return path** — if it raises questions for *you*, they should **inject a reverse memo back into your repo**. Name your repo so they can.

3. **Inject it** (create the label first if needed):
   ```bash
   gh issue create --repo <target-owner>/<target-repo> \
     --title "Interoffice memo (from <Your Division>): <one-line want>" \
     --label "interoffice-memo" \
     --body-file <memo.md>
   ```

4. **Stop there.** The memo is enqueued intent. Do **not** follow it into their repo, open a PR against them, or drive their shift. Your job ends at *send*; theirs begins at *their next shift*.

## Receiving a memo

Your shift encounters an issue labeled `interoffice-memo` (surface them with `gh issue list --label interoffice-memo --state open`). This is another division asking *you* for something. It is **yours to adjudicate** — you are the only actor with your division's full context.

1. **Recognize it for what it is.** It is a *want from outside*, not an order and not a self-authored backlog item. You are not obligated to do exactly what it says. You **are** obligated to consider it and respond — silently dropping a memo breaks the bus.

2. **Adjudicate on your own terms.** Decide **how**, or **whether**, to act, and sequence it against your own backlog like any other work. Reasonable outcomes:
   - **Accept & schedule** — it's good and fits; triage it into a shift like normal work (it may spawn your own issues/PRs). Comment to acknowledge and say when/how.
   - **Accept with changes** — you'll address the underlying want a different way than proposed; say so.
   - **Decline / defer** — it conflicts with your direction or isn't worth it now; say why, and close or park it.
   In every case, **leave a comment** recording the decision so the sender (and any future shift) can see how the memo was handled.

3. **Use the return path when it raises questions.** If handling the memo surfaces something the *sending* division must decide or change — a constraint you can't meet, a canon change you need from them, a clarification — **send a reverse memo**: inject an `interoffice-memo` issue back into *their* repo (the "Sending a memo" steps above, pointed the other way). This is normal; coordination is bidirectional. Don't stall your shift waiting on them — enqueue the reverse memo and keep moving.

4. **Close when resolved.** A memo is done when its want has been accepted-and-actioned, addressed-another-way, or declined — with the outcome recorded in a comment. Don't close a memo just because it's inconvenient; that's the orphan-close failure mode (an unresolved request silently dropped).

## The one rule under all of it

**No division reaches into another division's tree.** Every cross-project effect flows through a labeled issue that the target's orchestrator adjudicates. Requester supplies the want; the division decides the how. If you catch yourself about to edit, PR, or drive another repo directly — stop and send a memo instead.
