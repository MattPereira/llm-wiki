# ADR-0001: Split immutable `raw/` from agent-owned `wiki/`

**Status:** accepted · 2026-09-06

## Context

Ingested sources landed in `content/`, organised by platform. There was no
distillation layer yet, and no rule about who was allowed to write where.

The obvious alternative was one file per source holding the summary above the full
text — it keeps the two together and matches "show me both" directly.

## Decision

Two directories. `raw/` holds verbatim fetched artifacts; only the ingest scripts
write there. `wiki/` holds distillations; only the agent writes there.

Paths mirror, so the mapping is mechanical in both directions and a script can find
orphans or re-distill in bulk without parsing frontmatter.

`content/` renamed to `raw/` (commit `9aac8a3`).

## Consequences

Rejected the single-file layout because the two have different lifecycles. A raw
file is fetched once and often cannot be re-fetched — YouTube auto-transcripts
disappear. A distill is regenerated every time the prompt improves. Colocating them
means every re-distill rewrites the source of truth, puts a 7,400-word essay in the
diff of every prompt tweak, and gives one frontmatter block two owners.

Inputs are not rewritten by the things that consume them.

Side-by-side reading survives: the wiki page links to its raw file, and Obsidian
transclusion inlines the full text under the summary if that is wanted literally.

This is the [Karpathy LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
which all four reference implementations in `README.md` follow.
