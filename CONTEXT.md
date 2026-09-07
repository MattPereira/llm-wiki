# Context

## Purpose

Too much long-form content to read. This repo ingests it and summarizes it, so the
human reads summaries instead of sources.

It is equally an experiment in *how* to do that. When "save the human time" and
"learn to build this well" conflict, neither automatically wins — but a design that
saves no time has failed, because an unused wiki teaches nothing.

## Language

- **Wiki** — the whole knowledge store: `wiki/`, holding both layers below. The repo
  around it (`scripts/`, `docs/`, `creators.toml`) is tooling, not wiki.
- **Raw** — a fetched source document, verbatim. Lives in `wiki/raw/`. Immutable.
- **Summary** — an agent-written summary of one raw document. Lives in
  `wiki/summaries/`. Regenerable.
- **Source** — one raw document (a video, a post). The unit of ingestion, and the
  unit of summarization: one source, one summary. See ADR-0003.
- **Creator** — a single editorial identity that publishes, regardless of how many
  humans are behind it. Kyla Scanlon is a creator; so are 1000x and Steady Lads.
  The folder key inside `wiki/raw/` and `wiki/summaries/`. See ADR-0006.
- **Medium** — YouTube transcript vs. Substack post. Carried in the `type`
  frontmatter field of the raw file. Determines what a summarizer *ignores*.
- **Genre** — the shape of a piece: earnings review, single-asset thesis, macro
  essay, monthly recap, multi-topic podcast. Determines what a summarizer *emits*.
  Creator is a proxy for genre, not the same thing — Kyla writes both 3-minute
  shorts and 7,000-word essays.
- **Extract** — the ignore-rules half of summarization. Medium-specific.
- **Summarize** — the emit-a-shape half. Genre-specific, routed by creator.

## Layers

The [Karpathy LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
three layers:

```
wiki/raw/        immutable fetched artifacts  — scripts write, nothing else edits
wiki/summaries/  agent-owned summaries        — regenerable; the human reads, never writes
AGENTS.md        the schema                   — how the agent maintains the other two
```

`wiki/raw/` is the source of truth and is not reproducible. Move files with `git mv`;
never regenerate them.

`wiki/summaries/` is disposable by design. Improving a summary means changing the
prompt and regenerating, not hand-editing the output — that is what makes bulk
re-runs a usable way to evaluate a prompt change. See ADR-0004.

It is also the [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format)
bundle root: every file under it is a concept carrying conformant frontmatter.
`wiki/raw/` sits deliberately outside, because a verbatim transcript is not a
concept. See ADR-0001.

## Summarization

One agent pass per source, one output file. Two sets of rules compose inside it:

1. **Extract** (by medium) — what to ignore. Spoken transcripts: banter, `[music]`,
   sponsor reads; preserve speaker attribution where a source is a dialogue.
   Substack: disclaimers, follow/subscribe links, translation links.
2. **Summarize** (by genre) — what to emit. One base shape, plus a per-creator
   override where the genre demands different fields.

Written separately so the ignore-rules are authored once per medium rather than
copy-pasted into every creator's skill. Not separate files on disk. See ADR-0003.

Every summary records when it was generated and by which version of the skill, in
OKF's `generated` field. Without that, "did the prompt get better?" is unanswerable
a month from now.

## Phases

Each phase is gated: build it when the gate opens, not before.

| # | Build | Gate |
|---|---|---|
| 0 | Ingest scripts | **done** |
| 1 | Per-source summaries in `wiki/summaries/` | now |
| 2 | Rolling digest across sources | ~15 sources, summaries that are trusted |
| 3 | Auto-pull new posts/videos on release | digests get read unprompted |
| 4 | Cross-source synthesis (`wiki/topics/`) | ~50 sources |
| 5 | Frontend | Markdown demonstrably failing |

Phase 4 is where "Hayes and Taiki disagree about Q4 liquidity" becomes findable. It
is phase 4 because it is worthless on nine sources.

Deferred until they solve a problem that actually exists: `index.md` (a catalog the
agent reads before searching), `log.md` (append-only ingest history), a search index,
and any frontend. Both are OKF reserved filenames, so adopting them later is additive.
At current scale `ls wiki/raw/` is the index and `git log` is the log.
