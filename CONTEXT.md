# Context

## Purpose

Too much long-form content to read. This repo ingests it and distills it, so the
human reads summaries instead of sources.

It is equally an experiment in *how* to do that. When "save the human time" and
"learn to build this well" conflict, neither automatically wins — but a design that
saves no time has failed, because an unused wiki teaches nothing.

## Language

- **Raw** — a fetched source document, verbatim. Lives in `raw/`. Immutable.
- **Wiki** — an agent-written distillation. Lives in `wiki/`. Regenerable.
- **Source** — one raw document (a video, a post). The unit of ingestion.
- **Creator** — the person or publication a source comes from. Currently the folder
  key inside `raw/`, split per platform. See ADR-0005.
- **Medium** — YouTube transcript vs. Substack post. Carried in the `type`
  frontmatter field. Determines what a distiller *ignores*.
- **Genre** — the shape of a piece: earnings review, single-asset thesis, macro
  essay, monthly recap, multi-topic podcast. Determines what a distiller *emits*.
  Creator is a proxy for genre, not the same thing — Kyla writes both 3-minute
  shorts and 7,000-word essays.
- **Extract** — the ignore-rules half of distillation. Medium-specific.
- **Distill** — the emit-a-shape half. Genre-specific, routed by creator.

## Layers

The [Karpathy LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
three layers:

```
raw/        immutable fetched artifacts     — scripts write, nothing else edits
wiki/       agent-owned distillations       — regenerable; the human reads, never writes
AGENTS.md   the schema                      — how the agent maintains the other two
```

`raw/` is the source of truth and some of it is not re-fetchable (YouTube
auto-transcripts disappear). Move those files with `git mv`; never regenerate them.

`wiki/` is disposable by design. Improving a distill means changing the prompt and
regenerating, not hand-editing the output — that is what makes bulk re-runs a usable
way to evaluate a prompt change. See ADR-0004.

## Distillation

One agent pass per source, one output file. Two sets of rules compose inside it:

1. **Extract** (by medium) — what to ignore. Spoken transcripts: banter, `[music]`,
   sponsor reads; preserve speaker attribution where a source is a dialogue.
   Substack: disclaimers, follow/subscribe links, translation links.
2. **Distill** (by genre) — what to emit. One base shape, plus a per-creator
   override where the genre demands different fields.

Written separately so the ignore-rules are authored once per medium rather than
copy-pasted into every creator's skill. Not separate files on disk. See ADR-0003.

Every wiki page records `distilled_at` and the version of the skill that produced
it. Without that, "did the prompt get better?" is unanswerable a month from now.

## Phases

Each phase is gated: build it when the gate opens, not before.

| # | Build | Gate |
|---|---|---|
| 0 | Ingest scripts | **done** |
| 1 | Per-source distills in `wiki/` | now |
| 2 | Rolling digest across sources | ~15 sources, distills that are trusted |
| 3 | Auto-pull new posts/videos on release | digests get read unprompted |
| 4 | Cross-source synthesis (`wiki/topics/`) | ~50 sources |
| 5 | Frontend | Markdown demonstrably failing |

Phase 4 is where "Hayes and Taiki disagree about Q4 liquidity" becomes findable. It
is phase 4 because it is worthless on nine sources.

Deferred until they solve a problem that actually exists: `index.md` (a catalog the
agent reads before searching), `log.md` (append-only ingest history), a search index,
and any frontend. At current scale `ls raw/` is the index and `git log` is the log.
