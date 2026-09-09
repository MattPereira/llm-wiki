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
