#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch a YouTube transcript and write it as Markdown into wiki/raw/<creator>/.

Usage:  uv run scripts/ingest_youtube.py <url> [--force]
Prints the written path on stdout. Everything else goes to stderr.

Exit codes: 0 ok (or already ingested), 1 fetch failed, 2 no transcript,
3 rate limited by YouTube.
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from creators import RAW_DIR, ROOT, resolve, target

YT_DLP_VERSION = "2026.08.19"  # pinned: YouTube breaks stale yt-dlp builds outright
BLOCK_MS = 60_000  # target paragraph length; blocks always end on a sentence boundary
SNAP_MS = 20_000  # chapter marks routinely land mid-sentence; hunt this far for a sentence end

EXIT_FETCH, EXIT_NO_TRANSCRIPT, EXIT_RATE_LIMITED = 1, 2, 3

# Each language key costs a separate timedtext request, so ask for exactly one.
# "en-orig" is the original-language ASR track; yt-dlp only ever builds it without a
# "tlang", so it can never be a machine translation. Plain "en" is the same track when
# the audio is English but silently becomes a translation of the ASR when it is not
# (yt_dlp/extractor/youtube/_video.py, the "-orig" branch). Videos whose original audio
# YouTube marks as something else have no "en-orig" -- those exit 2, re-run with "en".
# This also rules out human-written subs: --sub-langs filters those by the same key and
# they are only ever registered under a plain code, so --write-subs could never match.
SUB_LANGS = "en-orig"

LOG_DIR = ROOT / ".logs" / "yt-dlp"  # gitignored; -v stderr from every fetch
# Do not add --print-traffic here: it sets http.client's debuglevel, which print()s to
# stdout, corrupting the --dump-single-json payload this script parses from stdout.

# Header values worth scrubbing before anything lands on disk. Plain -v rarely emits
# these, but yt-dlp can echo request headers both as plain lines and inside repr'd byte
# blobs where the separator is a literal backslash-r-backslash-n, so the value runs to
# whichever terminator comes first. Cheap insurance on a file we write unattended.
SECRET_HEADERS = r"(?:Set-)?Cookie|Authorization|X-Goog-[\w-]+|X-Youtube-[\w-]+|X-Origin"
# The delimiter must be matched explicitly rather than with \b: inside a repr'd blob the
# character preceding a header name is the "n" of a literal backslash-n, which is a word
# character, so there is no boundary there to anchor on.
REDACT_RE = re.compile(
    rf"(?i)(^|[\s;,]|\\r\\n)({SECRET_HEADERS})(\s*:\s*)([^\r\n]*?)(?=\\r\\n|[\r\n]|$)",
    re.M,
)

RATE_LIMIT_RE = re.compile(r"429|Too Many Requests", re.I)


def yt_dlp_diagnostics(err: str) -> str:
    """The actionable part of a yt-dlp failure: its ERROR/WARNING lines.

    yt-dlp reports the HTTP status, any Retry-After, and its own retry attempts on
    these lines; everything else is progress noise. Falls back to the tail so a
    failure shaped differently than expected still leaves something to read.
    """
    lines = [ln.strip() for ln in err.splitlines() if ln.strip()]
    keep = [ln for ln in lines if ln.startswith(("ERROR:", "WARNING:")) or RATE_LIMIT_RE.search(ln)]
    return "\n".join(dict.fromkeys(keep or lines[-5:]))


def die(code: int, msg: str):
    print(msg, file=sys.stderr)
    sys.exit(code)


def slugify(text: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")[:80].strip("-")
    return slug or fallback


def human_duration(seconds) -> str:
    if not seconds:
        return "?"
    s = int(seconds)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def video_format(meta: dict) -> str:
    """Either "short" or "video", from the frame shape -- shorts are vertical.

    Not from duration: the 3-minute shorts ceiling overlaps ordinary short landscape
    uploads, so a threshold would mislabel both ways. Not from the URL either, since
    yt-dlp normalises /shorts/<id> to /watch?v=<id> before we ever see it.
    """
    return "short" if (meta.get("aspect_ratio") or 1) < 1 else "video"


def log_stderr(url: str, err: str) -> Path | None:
    """Persist yt-dlp's -v stderr so request counts stay auditable after the run.

    Secret header values are scrubbed first; request/response lines are left intact so
    the traffic stays countable. Best-effort: a logging failure must never sink an
    otherwise good ingest.
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = LOG_DIR / f"{stamp}-{video_id_from_url(url) or 'unknown'}.log"
        scrubbed = REDACT_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}[REDACTED]", err)
        path.write_text(f"# {url}\n{scrubbed}\n", encoding="utf-8")
        return path
    except OSError:
        return None


def fetch(url: str, workdir: Path) -> dict:
    """One yt-dlp pass: writes json3 subs into workdir, returns the metadata dict.

    --dump-single-json implies --simulate, which silently skips writing the
    subtitle files; --no-simulate is what makes both happen in one call.
    """
    cmd = [
        "uvx", "--from", f"yt-dlp=={YT_DLP_VERSION}", "yt-dlp", "-v",
        "--skip-download", "--no-simulate", "--dump-single-json",
        # --skip-download stops the media transfer but not format discovery, which still
        # fetches the HLS/DASH manifests. Nothing downstream reads formats, so skip both.
        "--extractor-args", "youtube:skip=hls,dash",
        "--write-auto-subs",
        "--sub-langs", SUB_LANGS, "--sub-format", "json3",
        "-P", str(workdir), "-o", "%(id)s.%(ext)s",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = log_stderr(url, proc.stderr)
    if proc.returncode != 0 or not proc.stdout.strip() or proc.stdout.strip() == "null":
        err = proc.stderr.strip()
        if RATE_LIMIT_RE.search(err):
            detail = textwrap.indent(yt_dlp_diagnostics(err), "  ")
            die(EXIT_RATE_LIMITED,
                f"rate limited by YouTube, wait a few minutes\nyt-dlp stderr:\n{detail}"
                + (f"\nfull log: {log}" if log else ""))
        die(EXIT_FETCH, f"fetch failed: {err.splitlines()[-1] if err else 'no output from yt-dlp'}"
            + (f"\nfull log: {log}" if log else ""))
    return json.loads(proc.stdout)


def track_path(meta: dict, workdir: Path) -> Path | None:
    """The one subtitle file this fetch asked for, if yt-dlp actually wrote it."""
    path = workdir / f"{meta['id']}.{SUB_LANGS}.json3"
    return path if path.exists() else None


def to_words(events: list) -> list[tuple[int, str]]:
    words = []
    for ev in events:
        # aAppend events are rolling-caption repeats; including them duplicates text
        if ev.get("aAppend") or not ev.get("segs"):
            continue
        for seg in ev["segs"]:
            text = seg.get("utf8", "").strip()
            if text:
                words.append((ev["tStartMs"] + seg.get("tOffsetMs", 0), text))
    return words


def to_paragraphs(words: list, until_ms: int | None = None) -> list[str]:
    """Fill to BLOCK_MS, then break at the next sentence end. Purely for readability:
    the break points carry no meaning, unlike chapter boundaries."""
    paragraphs, current, start = [], [], None
    for at, word in words:
        if until_ms is not None and at >= until_ms:
            break
        if start is None:
            start = at
        current.append(word)
        if at - start >= BLOCK_MS and word.endswith((".", "?", "!")):
            paragraphs.append(" ".join(current))
            current, start = [], None
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def snap_to_sentence(words: list, index: int, floor: int) -> int:
    """Slide a chapter boundary to the nearest sentence start within SNAP_MS.

    Creators drop chapter marks by ear, so the mark usually lands a few words into
    a sentence -- cutting there strands its opening under the previous heading and
    starts the section mid-clause. Search outward from the raw index for a word whose
    predecessor ends a sentence, staying inside SNAP_MS and never crossing `floor`
    (the previous boundary). Auto transcripts are sometimes unpunctuated for minutes
    at a time; then no candidate exists and the raw index stands.
    """
    at = words[index][0]
    for offset in range(len(words)):  # offset 0 first: a mark already on a sentence start stays put
        for candidate in (index - offset, index + offset):
            if candidate <= floor or candidate >= len(words):
                continue
            if abs(words[candidate][0] - at) > SNAP_MS:
                continue
            if words[candidate - 1][1].endswith((".", "?", "!")):
                return candidate
        if index - offset <= floor and index + offset >= len(words):
            break
    return index


def to_sections(words: list, chapters: list | None) -> list[tuple[str | None, list[str]]]:
    """Creator/YouTube chapters become real sections; without them, one untitled run."""
    if not chapters:
        return [(None, to_paragraphs(words))]

    # Boundaries as word indices, not timestamps: snapping moves a boundary past
    # words either way, which slicing by index expresses and filtering by time can't.
    bounds, floor = [], 0
    for chapter in chapters[1:]:
        start_ms = int((chapter.get("start_time") or 0) * 1000)
        raw = next((i for i, w in enumerate(words) if w[0] >= start_ms), len(words))
        floor = snap_to_sentence(words, raw, floor) if 0 < raw < len(words) else raw
        bounds.append(floor)

    sections = []
    for chapter, start, end in zip(chapters, [0] + bounds, bounds + [len(words)]):
        paragraphs = to_paragraphs(words[start:end])
        if paragraphs:
            sections.append((chapter.get("title") or "Untitled", paragraphs))
    return sections or [(None, to_paragraphs(words))]


def video_id_from_url(url: str) -> str | None:
    """The id as it appears in a watch/share/embed URL, or None if it isn't one."""
    match = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


def already_ingested(video_id: str):
    for path in RAW_DIR.rglob("*.md"):
        if f"video_id: {video_id}" in path.read_text(encoding="utf-8"):
            return path
    return None


def render(meta: dict, sections: list) -> str:
    vid = meta["id"]
    url = f"https://www.youtube.com/watch?v={vid}"
    raw_date = meta.get("upload_date") or ""
    date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}" if raw_date else ""
    channel = meta.get("channel") or meta.get("uploader") or "Unknown"
    title = meta.get("title") or vid
    titled = [s for s in sections if s[0] is not None]
    words = sum(len(p.split()) for _, paras in sections for p in paras)

    lines = [
        "---",
        "type: YouTube Transcript",
        f"format: {video_format(meta)}",
        f'title: "{title.replace(chr(34), chr(39))}"',
        f'channel: "{channel.replace(chr(34), chr(39))}"',
        f"url: {url}",
        f"video_id: {vid}",
        f"upload_date: {date}",
        f"duration: {meta.get('duration') or 0}",
        f"chapters: {len(titled)}",
        f"fetched_at: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"word_count: {words}",
        "---",
        "",
        f"# {title}",
        "",
        f"**{channel}** · {date} · {human_duration(meta.get('duration'))} · [watch]({url})",
        "",
    ]
    if not titled:
        lines += ["## Transcript", ""]
    for heading, paragraphs in sections:
        if heading is not None:
            lines += [f"## {heading}", ""]
        for paragraph in paragraphs:
            lines += [paragraph, ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ingest a YouTube transcript as Markdown.")
    parser.add_argument("url")
    parser.add_argument("--force", action="store_true", help="re-ingest even if already present")
    args = parser.parse_args()

    def skip(existing: Path) -> None:
        print(f"already ingested: {existing}", file=sys.stderr)
        print(existing)

    # Check before fetching where the URL carries the id: a fetch is the throttled
    # resource, and backfill re-offers already-ingested videos on every run.
    vid = video_id_from_url(args.url)
    if vid and not args.force:
        existing = already_ingested(vid)
        if existing:
            return skip(existing)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        meta = fetch(args.url, workdir)

        # Still needed: playlist and redirect URLs carry no id to check up front.
        existing = already_ingested(meta["id"])
        if existing and not args.force:
            return skip(existing)

        track = track_path(meta, workdir)
        if track is None:
            die(EXIT_NO_TRANSCRIPT,
                f"no English transcript available for {meta['id']} "
                f"(asked for {SUB_LANGS}); if the video has captions, "
                f're-run with SUB_LANGS="en"')

        words = to_words(json.loads(track.read_text(encoding="utf-8")).get("events", []))
        if not words:
            die(EXIT_NO_TRANSCRIPT, f"transcript for {meta['id']} was empty")
        sections = to_sections(words, meta.get("chapters"))

        raw_date = meta.get("upload_date") or ""
        date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}" if raw_date else "undated"
        channel = slugify(meta.get("channel") or meta.get("uploader") or "", meta["id"])
        path = target(
            resolve("youtube", channel),
            f"{date}-{slugify(meta.get('title') or '', meta['id'])}.md",
            f"video_id: {meta['id']}",
        )
        path.write_text(render(meta, sections), encoding="utf-8")

    print(path)


if __name__ == "__main__":
    main()
