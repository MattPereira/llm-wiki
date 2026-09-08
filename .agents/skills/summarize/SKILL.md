---
name: summarize
version: 1
description: How to summarize and process content from /wiki/raw/
---

# Process

## 1. Summarize the content of the raw source

For youtube videos, ignore pleasantries and banter unrelated to core content. The youtube transcripts are raw and may contain spelling and other types of errors.

## 2. Save the summary to `wiki/summaries/<creator>/<date>-<title>.md`

Start the file with YAML front matter

```yaml
---
type: summary
agent: codex
source: ../../raw/<creator>/<date>-<title>.md
title: "Source title"
creator: "Creator name"
host: "Host name"
guests: ["Guest name"]
url: https://example.com/source
upload_date: YYYY-MM-DD
---
```
