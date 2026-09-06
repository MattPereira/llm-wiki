# ADR-0004: `wiki/` is agent-owned and regenerable; never hand-edited

**Status:** accepted · 2026-09-06

## Context

Distill quality is the open question of this project, and judging it is slow — it
means reading summaries, then the sources, over weeks. Prompts will be tweaked
continuously over that period.

## Decision

The agent owns `wiki/` entirely. To correct a distill, change the prompt and
regenerate; do not edit the output. Human notes belong elsewhere.

Every wiki page carries `distilled_at` and the version of the skill that produced it.

## Consequences

Keeping distills disposable is what makes evaluating a prompt change tractable:
re-run across all sources and diff. One hand-edit breaks that, because the next bulk
regeneration destroys the edit — and after it happens once, bulk regeneration stops
being used.

The provenance fields are the entire evidence base for the experiment. Without them,
a mediocre summary read a month from now cannot be attributed to the current prompt
or to a version already fixed. This is the part of the `log.md` convention worth
keeping while deferring the rest.

Follows Karpathy's rule for the wiki layer: "You read it; the LLM writes it."
