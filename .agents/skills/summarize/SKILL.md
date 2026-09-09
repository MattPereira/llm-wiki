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
blurb: "One sentence saying what this source argues."
topics: ["macro", "crypto-markets"]
---
```

`blurb` and `topics` are required on every summary — the reading site's content
schema rejects a summary missing either.

### blurb

One sentence ending in a period, written for someone deciding whether to open the
summary. Say what the source argues, not what it is about:
"Maeda favors gradual accumulation into the bottom." beats "A video about crypto
markets." Name the people and tickers that carry the argument.

### topics

Pick from the slugs defined in `topics.toml` at the repo root, reading each entry's
comment to find where its boundary sits. Apply every Topic that genuinely fits, and
none that only nearly fit — one or two is normal, four means you are stretching.

**Never invent a Topic.** If nothing in `topics.toml` fits, stop and ask the user
whether to add one, proposing a slug, display name, and the boundary comment that
would go with it. Only edit `topics.toml` after they say yes. A vocabulary that
grows a Topic per summary is worse than no vocabulary.
