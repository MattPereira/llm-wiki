# Context

Glossary for the LLM wiki. Terms only — no implementation details, no decisions.
Decisions live in `docs/adr/`.

## Creator

A person or publication whose output is ingested. Identified by a **creator slug**
(`kyla-scanlon`, `1000x`) which is the folder name under `wiki/raw/` and
`wiki/summaries/`. `creators.toml` maps platform-derived slugs to the canonical one
and carries the human-readable name.

Not "author", not "source" — a Creator publishes many Sources.

## Source

The original third-party artifact: one Substack post, one YouTube video. Lives
outside this repo; identified by its `url`. The wiki never owns a Source, only
points at it.

## Raw

A near-verbatim capture of one Source as markdown with frontmatter, under
`wiki/raw/<creator>/<date>-<slug>.md`. Agent input, not human reading material.
One Raw per Source.

## Summary

An agent-written condensation of exactly one Raw, under
`wiki/summaries/<creator>/<date>-<slug>.md`, linked back by its `source:` field.
The human-facing artifact. A Raw may have no Summary yet; a Summary always has a Raw.

## Index

`wiki/index.md` — the navigational listing of every Summary, grouped by Creator.
Exists so an agent entering a fresh session can see the whole wiki in one read.
Generated from Summary frontmatter, never hand-written.

## Log

`wiki/log.md` — the append-only journal of ingest and summarize runs, including
what went wrong. A changelog, not a content artifact.

## Site

The deployed web front-end that renders Summaries for human reading. A pure
projection of the markdown files: it never becomes a second source of truth for
wiki content.

## Blurb

A one-sentence description of a Summary, written by the agent that wrote the
Summary and stored in its frontmatter. Serves both human scanning on the Site and
agent navigation via the Index. One per Summary.

## Topic

A term from the controlled vocabulary defined in `topics.toml`, attached to a Summary,
used to browse across Creators. Distinct from a free-form tag: an agent may only apply
an existing Topic, and must ask before a new one is added to the vocabulary.
