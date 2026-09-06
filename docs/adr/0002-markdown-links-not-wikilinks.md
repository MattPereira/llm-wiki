# ADR-0002: Standard Markdown links, not `[[wikilinks]]`

**Status:** accepted · 2026-09-06

## Context

The reference implementations split. `ar9av/obsidian-wiki` mandates `[[wikilinks]]`
— Obsidian-native, better graph view. Google's Open Knowledge Format mandates
standard Markdown links for portability.

This read as a choice between OKF and Obsidian. It is not: OKF is a frontmatter
convention, Obsidian is an application that reads Markdown folders. Obsidian renders
both link styles. They compose.

## Decision

Standard Markdown links in `wiki/`.

## Consequences

GitHub is the phase-1 read surface and it renders only Markdown links; wikilinks
would commit to Obsidian before Obsidian has been chosen.

Cheap to revisit. Because paths mirror (ADR-0001), `[[foo]]` <-> `[foo](path/foo.md)`
is one regex across the wiki, in either direction.

Cost: no Obsidian graph view unless converted. Acceptable — there is no graph worth
viewing until phase 4.
