---
name: ingest
version: 1
description: How to ingest new sources of information into the wiki/ directory
---

# Process

## 1. Execute the appropriate ingestion script
Examine the user provided URL to discern the type of content

- Call the `scripts/ingest_youtube.py` script if the URL contains `youtube.com`
- Call the `scripts/ingest_substack.py` script if the URL contains `youtube.com`

## 2. Call the skill tool with "summarize"

## 3. Update the `wiki/index.md` file 

Add a link to the newly created summary page and a one line summary of the summary page

**Example:**
```md
- [Atención](summaries/arthur-hayes/2026-09-02-atencion.md) — 2026-09-02 · Arthur Hayes — Hayes argues falling EUR/JPY will precede major dollar-liquidity expansion.
```

## 4. Append an entry to `wiki/log.md` 

**Example:**
```md
## [2026-09-07] ingest | Atención
  - Added: [summary](summaries/arthur-hayes/2026-09-02-atencion.md)
  - Notes: Added Hayes’s dollar-liquidity thesis; no contradictions found.
```
