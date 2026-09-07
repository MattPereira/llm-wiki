# ADR-0004: `wiki/summaries/` is agent-owned and regenerable; never hand-edited

**Status:** accepted · 2026-09-06

## Context

Summary quality is the open question of this project, and judging it is slow — it
means reading summaries, then the sources, over weeks. Prompts will be tweaked
continuously over that period.

## Decision

The agent owns `wiki/summaries/` entirely. To correct a summary, change the prompt and
regenerate; do not edit the output. Human notes belong elsewhere.

Every summary carries OKF's `generated: {by, at}` — the skill version that wrote it
and when.

## Consequences

Keeping summaries disposable is what makes evaluating a prompt change tractable:
re-run across all sources and diff. One hand-edit breaks that, because the next bulk
regeneration destroys the edit — and after it happens once, bulk regeneration stops
being used.

The provenance fields are the entire evidence base for the experiment. Without them,
a mediocre summary read a month from now cannot be attributed to the current prompt
or to a version already fixed. This is the part of the `log.md` convention worth
keeping while deferring the rest, and OKF v0.2 already has a field for it.

Existence of the mirrored path is the whole bookkeeping record: `comm` over
`find wiki/raw` and `find wiki/summaries` yields gaps and orphans, and re-summarizing
means deleting and re-running. The ingest scripts' overwrite guard is deliberately not
mirrored here — it exists because a raw artifact is not re-fetchable, which is the
opposite of the case for a summary.

No orchestrator yet: the skill is invoked per source by hand, one fresh context each,
until re-running the corpus by hand actually hurts. The loop that replaces it is a
shell `for` over `find wiki/raw`, so it stays runnable from Codex as well as Claude.

Follows Karpathy's rule for the wiki layer: "You read it; the LLM writes it."
