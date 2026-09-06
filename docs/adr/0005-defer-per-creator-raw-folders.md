# ADR-0005: Keep `raw/` organised by platform, for now

**Status:** superseded by [ADR-0006](./0006-raw-organised-per-creator.md) · 2026-09-06

## Context

`raw/` is organised by platform, so a creator publishing on two platforms lands in
two trees under two slugs. Kyla Scanlon is both `raw/youtube/kyla-scanlon/` and
`raw/substack/kyla/` — one person, two folders.

The value model here is per-person ("what is Kyla's current thesis", "where do Hayes
and Taiki disagree"), so the hierarchy fights the way the wiki gets queried. Platform
is a property, and properties belong in frontmatter — where `type` already carries it.

## Decision

Organise by creator eventually; not yet. Platform folders stay for now.

## Consequences

The merge is not free. Both ingest scripts derive the output folder from platform
metadata — `slugify(channel)` for YouTube, the publication subdomain for Substack —
so it needs a creator identity map that knows "Kyla Scanlon" the channel and "Kyla's
Newsletter" the publication are one folder, plus a fallback policy for unmapped
creators.

Deferred so the first distillation experiment happens sooner. Cost of waiting is low
at nine files and rises with each ingest.

Superseded the same day. The deferral priced the merge as needing a display-name
identity map and an unmapped-creator policy; ADR-0006 needs neither.
