# The Lifecycle

A project does not start graveyard-ready. It earns that state by passing through three phases. The middle one — the externalization event — is the whole game; the rest is setup and payoff.

For the thesis and the placement rule these phases serve, see [operating-model.md](operating-model.md).

## 1. Inception — live, in the main thread

Ray and Claude work together in the main conversation. The shape is unknown, decisions fly, and knowledge is **legitimately ephemeral-in-chat**. This is the one phase where the transcript is an acceptable home for what's true, because the work is *being decided*, not *being run*. Don't fight it here — the cost of premature ceremony is real, and inception is where judgment, not durability, is the scarce thing.

The trap is staying here. A project that never leaves inception keeps all its knowledge in transcripts and heads, which means it can only be advanced by the people who were in the room. It cannot be handed to a cold agent on the graveyard shift.

## 2. The externalization event — the whole game

This is the **deliberate act of declaring a project graveyard-managed**. Everything currently living in heads and chat is dumped to durable substrate, each fact landing in its one home:

- backlog → **GitHub issues**
- technical canon → **repo docs** (`docs/ARCHITECTURE.md`, `docs/DECISIONS.md`)
- conventions / agent operating instructions → **`CLAUDE.md`**
- strategic state → a **Notion Project Overview** page

This is a ceremony, not a vibe. The skill **`externalize-project`** performs it — it walks the dump and lands each kind of knowledge in its home per [knowledge-homes.md](knowledge-homes.md).

**Step 2 happening *honestly* is the whole game.** "Honestly" means: no load-bearing knowledge left behind in a transcript or a memory file. If a fact the next agent needs still lives only in chat after externalization, the event didn't happen — it was theater. The test is brutal and simple: *could a cold agent, given only git + Notion, resume this project?* If the answer depends on something in your head or your transcript, you are not done.

## 3. The graveyard phase — self-describing, externally-driven

The project is now a **self-describing, externally-driven system**. Any shift, or any cold agent, resumes from **git + Notion alone**. Chat and local memory are **disposable by design** — you can clear the session, hand the next agent nothing but "get going on #N," and lose nothing, because everything that mattered is on disk in the system of record.

This is what makes the graveyard shift possible at all. The `graveyard-shift` skill drains the backlog assuming this contract holds; if step 2 was dishonest, the shift inherits the gap and either stalls or rebuilds lost context expensively. The lifecycle exists to guarantee the input that the working loop depends on.
