# ADR-0006: Organise `wiki/raw/` by creator, not platform

**Status:** accepted · 2026-09-06

## Context

The raw layer was organised by platform, so a creator publishing on two platforms
landed in two trees under two slugs — Kyla Scanlon was both `youtube/kyla-scanlon/`
and `substack/kyla/`, one person, two folders. Fixing it was first deferred as
expensive: a creator identity map plus a fallback policy for unmapped creators,
weighed against getting the first summarization experiment started.

That price was wrong. The map does not need to resolve "Kyla Scanlon" the channel
against "Kyla's Newsletter" the publication, because it never sees display names: it
is keyed on the slugs the scripts already derive (`slugify(channel)` for YouTube, the
publication subdomain for Substack). It is a rename table over today's folder names,
about fifteen lines, needing no new frontmatter and no new fetched data.

Creator is the primary key of this wiki. The queries that motivate it are per-creator
("what is Kyla's current thesis"), ADR-0001 mirrors `wiki/raw/` and `wiki/summaries/`
paths, and ADR-0003 routes the summarize stage by creator. A raw layer keyed on
platform is the only one that disagrees, so every summary pays a translation.

## Decision

```
wiki/raw/kyla-scanlon/2026-08-13-how-to-get-rich-in-america.md    # type: Substack Post
wiki/raw/kyla-scanlon/2026-08-28-fed-chair-kevin-warsh.md         # type: YouTube Transcript
```

One folder per creator, directly under `wiki/raw/`. Platform stays a property, carried
by the existing `type` field. `wiki/summaries/` mirrors, per ADR-0001.

`creators.toml` at the repo root maps platform-derived slugs to the canonical creator
slug. Renames append an alias and never edit one, so files already in `wiki/raw/` never
move twice. Folder slugs are hand-chosen — human name for a person, show name
otherwise — not derived from platform metadata.

An unmapped channel or subdomain auto-creates a folder from the derived slug and
prints a warning naming the file and the entry to add. Adding a creator is the most
frequent operation; a config that gates it would not survive contact.

## Consequences

No frontmatter changes and no backfill. The migration is `git mv` over nine files
plus a lookup in each script, which is the cheapest this will ever be — the cost of
the migration rises with every ingest, which is why deferring it further was wrong.

Rejected: a `--voice` CLI flag naming the creator per run. It resolves the collision
with no config file at all, but only while a human is at the terminal, and phase 3 is
unattended ingestion. Building it means building something scheduled for deletion.

Rejected: keying the map on stable platform IDs (YouTube `channel_id`, Substack
`publication_id`). Immune to renames, but it needs data the scripts do not capture,
and a file of `UC…` strings cannot be reviewed by reading it. Display-derived slugs
change rarely, and an alias line absorbs it when they do.

Merging platforms costs one accidental signal: the old `youtube/kyla-scanlon/` and
`substack/kyla/` folders sorted her 3-minute shorts from her 7,000-word essays, and
ADR-0003's per-creator summarize routing was reading that for free. Recovered by
routing on `(creator, type)`.

`wiki/raw/` is immutable and some artifacts are not re-fetchable. The migration moves files
with `git mv` and never re-runs an ingest to "fix" a path. Both scripts currently
write their output unconditionally; a merged folder makes a same-day slug collision
possible between platforms, so both now refuse to overwrite an existing file whose
ID does not match.
