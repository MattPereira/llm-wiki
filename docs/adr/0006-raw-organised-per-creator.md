# ADR-0006: Organise `raw/` by creator, not platform

**Status:** accepted · 2026-09-06 · supersedes ADR-0005

## Context

ADR-0005 accepted the platform-first layout with a known defect — one creator on two
platforms lands in two folders — and deferred the fix, pricing it as expensive: a
creator identity map plus a fallback policy for unmapped creators, weighed against
getting the first distillation experiment started.

That price was wrong. The map does not need to resolve "Kyla Scanlon" the channel
against "Kyla's Newsletter" the publication, because it never sees display names: it
is keyed on the slugs the scripts already derive (`slugify(channel)` for YouTube, the
publication subdomain for Substack). It is a rename table over today's folder names,
about fifteen lines, needing no new frontmatter and no new fetched data.

Creator is the primary key of this wiki. The queries that motivate it are per-creator
("what is Kyla's current thesis"), ADR-0001 mirrors `raw/` and `wiki/` paths, and
ADR-0003 routes the distill stage by creator. A `raw/` keyed on platform is the only
layer that disagrees, so every distill pays a translation.

## Decision

```
raw/kyla-scanlon/2026-08-13-how-to-get-rich-in-america.md    # type: Substack Post
raw/kyla-scanlon/2026-08-28-fed-chair-kevin-warsh.md         # type: YouTube Transcript
```

One folder per creator, directly under `raw/`. Platform stays a property, carried by
the existing `type` field. `wiki/` mirrors, per ADR-0001.

`creators.toml` at the repo root maps platform-derived slugs to the canonical creator
slug. Renames append an alias and never edit one, so files already in `raw/` never
move twice. Folder slugs are hand-chosen — human name for a person, show name
otherwise — not derived from platform metadata.

An unmapped channel or subdomain auto-creates a folder from the derived slug and
prints a warning naming the file and the entry to add. Adding a creator is the most
frequent operation; a config that gates it would not survive contact.

## Consequences

No frontmatter changes and no backfill. The migration is `git mv` over nine files
plus a lookup in each script, which is the cheapest this will ever be — the cost rises
with every ingest, which is what ADR-0005 already observed.

Rejected: a `--voice` CLI flag naming the creator per run. It resolves the collision
with no config file at all, but only while a human is at the terminal, and phase 3 is
unattended ingestion. Building it means building something scheduled for deletion.

Rejected: keying the map on stable platform IDs (YouTube `channel_id`, Substack
`publication_id`). Immune to renames, but it needs data the scripts do not capture,
and a file of `UC…` strings cannot be reviewed by reading it. Display-derived slugs
change rarely, and an alias line absorbs it when they do.

Merging platforms costs one accidental signal: `raw/youtube/kyla-scanlon/` and
`raw/substack/kyla/` sorted her 3-minute shorts from her 7,000-word essays, and
ADR-0003's per-creator distill routing was reading that for free. Recovered by
routing on `(creator, type)`.

`raw/` is immutable and some artifacts are not re-fetchable. The migration moves files
with `git mv` and never re-runs an ingest to "fix" a path. Both scripts currently
write their output unconditionally; a merged folder makes a same-day slug collision
possible between platforms, so both now refuse to overwrite an existing file whose
ID does not match.
