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
url: https://example.com/source
upload_date: YYYY-MM-DD
blurb: "One concise sentence saying what this source delivers."
topics: ["macro", "crypto-markets"]
---
```

`blurb` and `topics` are required on every summary — the reading site's content
schema rejects a summary missing either.

### blurb

One sentence, 25 words or fewer, ending in a period. It lets a reader — human or
agent — decide whether to open the summary without opening it. Say what the source
delivers, not what it covers: "Maeda favors gradual accumulation into the bottom."
beats "A video about crypto markets."

### topics

Pick from the slugs defined in `topics.toml` at the repo root, reading each entry's
comment to find where its boundary sits. Apply every Topic that genuinely fits, and
none that only nearly fit — one or two is normal, four means you are stretching.

**Never invent a Topic.** If nothing in `topics.toml` fits, stop and ask the user
whether to add one, proposing a slug, display name, and the boundary comment that
would go with it. Only edit `topics.toml` after they say yes. A vocabulary that
grows a Topic per summary is worse than no vocabulary.

## 3. Regenerate `wiki/index.md`

```sh
cd site && npm run generate-index
```

The Index is generated from Summary frontmatter — never hand-edit it. The command
fails naming the file and field if a Summary's frontmatter is invalid; fix the
frontmatter and rerun rather than editing the Index.
