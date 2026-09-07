# ADR-0001: Split immutable `wiki/raw/` from agent-owned `wiki/summaries/`

**Status:** accepted · 2026-09-06

## Context

Ingested sources landed in `content/`, organised by platform. There was no
summarization layer yet, and no rule about who was allowed to write where.

The obvious alternative was one file per source holding the summary above the full
text — it keeps the two together and matches "show me both" directly.

## Decision

Two directories under `wiki/`. `wiki/raw/` holds verbatim fetched artifacts; only the
ingest scripts write there. `wiki/summaries/` holds summaries; only the agent writes
there.

Paths mirror, so the mapping is mechanical in both directions and a script can find
orphans or re-summarize in bulk without parsing frontmatter.

`content/` renamed to `raw/` (commit `9aac8a3`), then moved under `wiki/`.

## Consequences

Rejected the single-file layout because the two have different lifecycles. A raw
file is fetched once and is not reproducible. A summary is regenerated every time the
prompt improves. Colocating them means every re-run rewrites the source of truth,
puts a 7,400-word essay in the diff of every prompt tweak, and gives one frontmatter
block two owners.

Inputs are not rewritten by the things that consume them.

Side-by-side reading survives: the summary links to its raw file, and Obsidian
transclusion inlines the full text under the summary if that is wanted literally.

### Why both sit under `wiki/`

Splitting by artifact kind at the top level is what the reference implementations do:
Karpathy's wiki layer is summaries, entity pages, concept pages, comparisons,
synthesis — kind first. Neither his gist nor the OKF spec prescribes a folder scheme
below that, so creator-first inside each kind (ADR-0006) is this repo's own choice.

The `wiki/` container separates content from tooling — `scripts/`, `docs/`,
`creators.toml`, `.claude/` stay outside it — which means an Obsidian vault can be
rooted at `wiki/` later with no file moves, and it gives `wiki/topics/` (phase 4) an
obvious home beside the other two.

It also gives the OKF bundle a root. Strict conformance treats every non-reserved
`.md` under the bundle as a concept requiring frontmatter, so the bundle is
`wiki/summaries/` alone: a verbatim 16k-word transcript is not a concept, and the
raw files' `type: YouTube Transcript` is a medium rather than a concept type. The
spec explicitly permits a bundle as a subdirectory of a larger repo.

Rejected `raw/` and `summaries/` as root-level peers. It keeps a fat-fingered
`rm -rf wiki/` from taking the irreplaceable corpus with the disposable one, but git
already covers that, and it forfeits the vault root for a risk that is cheap to undo.
