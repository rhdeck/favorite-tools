# Proposal: Tiered Multi-Agent Graveyard Shift (TAGS) Architecture

This document outlines a strategy for a tiered, multi-vendor execution engine for autonomous backlog work. The objective is to maximize resource efficiency and code quality by using a high-end reasoning model as the orchestrator/planner and cheaper models as concurrent code workers, gated by automated checks and budget constraints.

TAGS is a **separate initiative** from the Operating Model. It is the *engine* (how the fleet executes); the Operating Model is about *where truth lives* (knowledge homes / lifecycle). The existing [graveyard-shift](../../skills/graveyard-shift/SKILL.md) skill is one current consumer of these ideas, but TAGS is not part of that skill.

An interactive dashboard and flow diagram for this proposal can be opened here:
* [architecture.html](./architecture.html)

---

## 1. The Core Paradigm: Orchestration vs. Execution

Currently, the graveyard shift runs parallel subagents, but it does not cleanly segregate the model tiers used for planning versus implementation. By explicitly defining separate roles for different tiers of models, we can route work more efficiently:

| Model Tier | Representative Models | Primary Responsibility | Cost / Speed |
| :--- | :--- | :--- | :--- |
| **High-End (Planners)** | Codex (Extra High Thinking), Gemini Pro, Claude Opus (High) | Backlog triage, epic decomposition, worker specification, failure resolution | High cost / Slow |
| **Execution (Workers)** | Codex (Medium Thinking), Claude Sonnet / Opus (Medium), Gemini Pro | Code writing, test execution, compilation warning fixes, PR formatting | Low cost / Fast |
| **Utilities / Parsers** | Gemini Flash | Parsing log files, token counting, metadata extraction (not trusted to write code) | Extremely low cost / Instant |

### The Orchestrator Role
The orchestrator (high-reasoning model) has the context of the entire issue backlog. Rather than categorizing tasks as "trivial", it evaluates tasks as **Big / Architectural** (requiring Planners to shape/propose design first) vs. **Less Big / Bounded Implementation** (fanned out to workers).

For each issue:
1. It writes a structured **Job Spec** detailing the expected files to touch, tests to run, and explicit acceptance criteria.
2. It assigns a **Target Worker Model** based on the task's complexity (e.g. Gemini Pro or Claude Sonnet for coding).
3. It spawns the worker subagent with a lean, targeted context. Complex refactors and targeted implementation are not mutually exclusive; a complex refactor is decomposed by the Planner into targeted execution specs.

---

## 2. Dynamic Credit-Pacing & Multi-Vendor Budgets

To prevent credit overages and leverage vendor diversity, the orchestrator dynamically checks active subscription quotas and rate limits across Google, Anthropic, and OpenAI/Codex. 

### Budget Allocation Matrix
* **Gemini (Google)**: Gemini Pro for coding & planning (Flash relegated to log/text utility auditing, not trusted for code generation). Check Google Workspace/AI Studio tier token & rate quotas.
* **Claude (Anthropic)**: Claude Sonnet / Opus (Medium) for coding, Opus (High) for strategic planning. Verify Anthropic subscription limits dynamically.
* **OpenAI (Codex)**: Codex (Extra High Thinking) for planning & PR reviews, Codex (Medium Thinking) for execution. Track OpenAI API organization usage counters.

### Failover Rules
* If the active harness's budget is low or exhausted, the orchestrator automatically downgrades execution workers to cheaper equivalents (e.g., swapping a Claude Sonnet worker to a Codex Medium worker).
* If a reasoning model's quota is limited, the orchestrator queues strategic decisions for the next reset window while keeping mechanical workers running on other issues.

---

## 3. Quality Gates & Feedback Loops

To make lower-level models viable for code writing, we enforce rigorous automated testing and escalation paths.

```
[Spawn Worker] ──> [Apply Code] ──> [Run Tests & TSC]
                                           │
                                    ┌──────┴──────┐
                                 (Pass)        (Fail)
                                    │             │
                              [Codex-PR Loop]  [Iterate Limit Hit?]
                                    │             ├─────── Yes ──────> [Escalate to Pro]
                                 (Clean)       (No)                    (Triage error, rewrite spec)
                                    │             │
                                 [Merge]   [Refine Attempt]
```

### The Escalation Path
1. **Local Test Iteration**: A worker model (e.g., Codex Medium, Claude Sonnet, or Gemini Pro) attempts to fix code and rerun tests in a loop up to 3 times.
2. **Quality Gate Failure**: If compilation or tests still fail, the worker halts.
3. **Orchestrator Intervention**: The worker's failed diff and error logs are sent back to the orchestrator. The orchestrator determines whether:
   * The issue requires higher reasoning (escalates task to a Codex Extra High or Claude Opus worker).
   * The spec was wrong (corrects the spec and spawns a new worker).
   * The design is blocked (converts the task to a **Proposal** comment in the issue and flags the user).

---

## 4. Scaling Parallel Fleets

Concurrency and complexity are not mutually exclusive. We can kick off multiple complex refactors and targeted execution workers concurrently. This is exactly what git worktrees are designed for: isolating directories so parallel agents do not compete or clash.

* **Independent Worktrees**: Every worker subagent continues to run in its own git worktree (`.worktrees/issue-NNN/`) to prevent conflict merges.
* **Domain Isolation**: Planners ensure that fanned-out waves do not contain issues with overlapping files. If two issues modify `src/core/scan.ts`, they are sequenced serially instead of fanned out in parallel.
* **Complex Parallelism**: Multiple complex refactors can be processed simultaneously, each within its isolated worktree, maximizing throughput.
