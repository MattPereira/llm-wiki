# ADR-0007: A YouTube short is a `format`, not a separate `type`

**Status:** accepted · 2026-09-07

## Context

`wiki/raw/` carries one YouTube frontmatter type, `type: YouTube Transcript`, covering
both a 3-minute vertical short and an 80-minute interview. Nothing in a raw file
distinguishes them; the corpus already contains one short that reads as a video.

They do need different treatment. ADR-0003 anticipated exactly this — "ADR-0006 puts a
creator's 3-minute shorts and 7,000-word essays in one folder" — and CONTEXT.md's
vocabulary names the axis: creator is only a *proxy* for genre.

The obvious move is to split the type in two, `YouTube Video` / `YouTube Short`.

## Decision

Keep `type: YouTube Transcript` for both. Add a sibling field:

```yaml
type: YouTube Transcript
format: short        # or: video
```

Derived from the frame shape — shorts are vertical — via `aspect_ratio`, which yt-dlp
already returns in the metadata the ingest script fetches. No extra request.

Summarize rules key on `(creator, type, format)`, falling back to `(creator, type)`
where no format override exists. Extract rules keep keying on `type` alone.

## Consequences

Splitting `type` would have helped one half of ADR-0003 and hurt the other. Extract is
keyed on `type` alone, and its ignore-rules — auto-caption artifacts, pleasantries,
sponsor reads — are identical for a short and a long interview, because they are the
same medium. Doubling that keyspace buys nothing and costs the ADR-0003 property worth
protecting: ignore-rules are written twice, ever. Only the summarize half varies, and
`format` is the axis it varies on.

It also keeps `type` meaning what ADR-0001 says it means, "a medium rather than a
concept type". A short and a video are one medium.

Duration was rejected as the signal. The shorts ceiling is 3 minutes and ordinary
landscape uploads run shorter than that, so any threshold mislabels in both
directions. The URL was rejected too: yt-dlp normalises `/shorts/<id>` to
`/watch?v=<id>` before the script sees it. Frame shape is the one property that
survives both.

YouTube's own authoritative split is the `UULF`/`UUSH` playlist pair that
`scripts/backfill.py` already exploits for `long_form_only`. That is a listing-time
fact about a channel, unavailable when ingesting a single URL, so it cannot serve
here — but the two agree, which is the check on this heuristic.

The eight existing raw files were amended in place to add `format:`. `wiki/raw/` is
immutable as *content*; this is a purely additive schema migration with no re-fetch,
and leaving the corpus split between two frontmatter shapes would push the problem
into every future reader.
