---
name: ingest-youtube
description: Ingest a YouTube video into the wiki and give its transcript real structure. Use when adding a YouTube URL to content/, running scripts/ingest_youtube.py, or re-paragraphing and titling a transcript already ingested.
---

# Ingest a YouTube video

`scripts/ingest_youtube.py` fetches the transcript and writes the Markdown file. It breaks paragraphs on a 60-second timer and titles nothing the creator didn't title, so the file it writes is correctly worded and structurally meaningless. You supply the structure.

Two rules govern every edit you make to that file:

- **Verbatim** — the transcript's words are the artifact. You move whitespace and add `##` headings. Every other word survives exactly as the speaker said it, fillers and false starts included. Distillation happens downstream, against the verbatim record.
- **Beat** — one paragraph is one beat: a single claim and the evidence, example, or aside that serves it. The speaker moving to a new beat is the only reason a paragraph ends.
- **Straddle** — a heading dropped into the middle of something continuous, because the creator marked the chapter by ear. It takes three forms: a split **sentence**, a split **turn** (one speaker's `>>` block cut in half), or a split **thought** (both sides whole sentences, but the opener finishes the topic above it). The script snaps each boundary to the nearest sentence end within 20 seconds, so the sentence form is usually handled; the other two always reach you.

## Steps

### 1. Run the script

```
uv run scripts/ingest_youtube.py <url>
```

It prints the written path. On a non-zero exit: `1` fetch failed, `2` no English transcript (report it and stop — there is nothing to structure), `3` rate limited (wait a few minutes, retry). If it reports `already ingested`, the file exists and step 2 still applies; pass `--force` only to replace a file whose transcript itself is wrong.

Copy the file aside before you touch it — step 4 diffs against this copy:

```
cp <path> /tmp/ingest-before.md
```

### 2. Read the file and find the agenda

Read it end to end before editing. Speakers usually state their own outline in the first minute ("this will be the agenda for the video") and call their turns out loud ("the second reason is", "so let's rewind to"). Those phrases are the structure the video already has; your headings recover it rather than inventing a scheme over the top.

Frontmatter tells you which branch you're in: `chapters: N` means the creator titled the video.

### 3a. Chapters present — close the straddles, then re-paragraph

The `##` headings are the creator's: keep their text, and keep their order. At each one, read the last line above and the first line below as continuous speech and ask all three straddle questions: does a sentence carry across, does a `>>` turn carry across, does the opening line finish the topic above rather than start the one below? A section belongs to the speaker and topic it opens on, so move the straddling fragment to whichever side completes it. Word order never changes, so verbatim holds and step 4 stays clean.

Then, within each section, redraw the paragraph breaks onto beats.

### 3b. No chapters — title it, then re-paragraph

Replace the single `## Transcript` heading with headings at each topic shift a reader would navigate by, phrased in the speaker's own vocabulary from step 2. Aim for the granularity of a chapter list the creator would have written: a 3-minute video may be one or two, a 40-minute video is usually 5–10.

Then add `sections: agent` to the frontmatter, so downstream readers know the headings are yours and not the creator's.

### 4. Verify verbatim

Long transcripts run to thousands of words and edits drop text silently, so prove the words survived rather than trusting the edit:

```
diff <(scripts/transcript_words.sh /tmp/ingest-before.md) <(scripts/transcript_words.sh <path>)
```

The helper drops frontmatter and headings, so your headings and `sections: agent` are invisible to it and only the prose is compared. Empty diff means verbatim held. Any line it prints is a word you dropped, added, or altered — restore it from the copy before moving on.

Done when the diff is empty, no heading straddles a sentence, and every paragraph in the file is one beat.
