# ADR-0003: Distillation is medium-specific extract plus genre-specific emit

**Status:** accepted · 2026-09-06

## Context

Sources vary enormously, and the first instinct was one distillation skill per
creator. Reading `raw/` showed the variation does not fall on the creator axis.

Two YouTube files, opposite noise profiles: the 1000x podcast is 16,164 words of
two-person dialogue that opens on `>> Hello. >> How are you doing, Jonah?` and a
stretch about a haircut, with `[music]` markers throughout. Taiki is a scripted solo
monologue with essentially no filler after the first sentence.

Meanwhile Hayes has the same *class* of noise in Substack form — a disclaimer block,
Instagram/LinkedIn/X follow links, a translation link, a calendar subscribe link —
before the essay starts. Chrome, not banter, but the same job.

What genuinely varies per creator is output shape, and that tracks genre: Berbowski
writes earnings reviews (metrics vs. guidance, valuation multiples, thesis check),
Taiki writes single-asset theses, Hayes writes discursive macro essays, Crypto
Narratives writes monthly recaps.

## Decision

One agent pass per source producing one file, with two composed rule sets:

1. **Extract**, keyed on the `type` frontmatter field (`YouTube Transcript` /
   `Substack Post`) — what to ignore.
2. **Distill**, keyed on creator as a proxy for genre — what to emit. One base
   shape; per-creator overrides only where the genre demands different fields.

Both start as prompt sections, not files on disk.

## Consequences

One skill per creator would make each new creator independently re-solve "ignore the
pleasantries", and improving that logic would mean fixing it in seven places. Split
this way, ignore-rules are written twice, ever.

The extract stage must preserve speaker attribution for dialogue sources. Only 1000x
is a dialogue today, and "Avi said X, Jonah pushed back" is real signal that would
otherwise vanish silently.

Filler-stripping cannot move into `raw/`: the `ingest-youtube` skill enforces
verbatim and states that distillation happens downstream against that record.

No cleaned-transcript intermediate artifact. It would make re-running the distiller
on the 16k-word podcast cheaper, but it is a third copy of the corpus for a problem
not yet observed, and it is purely additive if ever wanted.
