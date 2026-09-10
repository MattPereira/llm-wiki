---
name: ingest
version: 1
description: How to ingest new sources of information into the wiki/ directory
---

# Process

## 1. Execute the ingestion script
- Call `uv run scripts/ingest.py <url>` with the user provided URL

## 2. Summarize the raw content
- Find the newly created raw source file and call the skill tool with "summarize"

## 3. Append an entry to `wiki/log.md` 

**Example:**
```md
## [2026-09-07] ingest | Atención
  - Added: [summary](summaries/arthur-hayes/2026-09-02-atencion.md)
  - Notes: Added Hayes’s dollar-liquidity thesis; no contradictions found.
```

## 4. Restart the dev server

The Astro dev server watches `site/` only, so nothing written to `wiki/` this run
is visible until it restarts. From `site/`:

```sh
pnpm exec astro dev status                 # is one running?
pnpm exec astro dev stop                   # only if it is
pnpm exec astro dev --background           # always
```

It comes back as a background server on port 4321 regardless of how it was
started, so `astro dev stop` also claims a server the user launched in their own
terminal. Logs: `pnpm exec astro dev logs --follow`.
