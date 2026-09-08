---
name: ingest
version: 1
description: How to ingest new sources of information into the wiki/ directory
---

# Process

## 1. Execute the ingestion script
Call `uv run scripts/ingest.py <url>` with the user provided URL

## 2. Summarize the raw content
- Find the newly created `wiki/raw/<creator>/<date>-<title>.md` file
- Call the skill tool with "summarize"

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
