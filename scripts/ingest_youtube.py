#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch a YouTube transcript and write it as Markdown into content/youtube/.

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
from pathlib import Path

YT_DLP_VERSION = "2026.08.19"  # pinned: YouTube breaks stale yt-dlp builds outright
BLOCK_MS = 60_000  # target paragraph length; blocks always end on a sentence boundary
SNAP_MS = 20_000  # chapter marks routinely land mid-sentence; hunt this far for a sentence end
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "youtube"

EXIT_FETCH, EXIT_NO_TRANSCRIPT, EXIT_RATE_LIMITED = 1, 2, 3


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


def fetch(url: str, workdir: Path) -> dict:
    """One yt-dlp pass: writes json3 subs into workdir, returns the metadata dict.

    --dump-single-json implies --simulate, which silently skips writing the
    subtitle files; --no-simulate is what makes both happen in one call.
    """
    cmd = [
        "uvx", "--from", f"yt-dlp=={YT_DLP_VERSION}", "yt-dlp",
        "--skip-download", "--no-simulate", "--dump-single-json",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en.*", "--sub-format", "json3",
        "-P", str(workdir), "-o", "%(id)s.%(ext)s",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip() or proc.stdout.strip() == "null":
        err = proc.stderr.strip()
        if "429" in err or "Too Many Requests" in err:
            die(EXIT_RATE_LIMITED, "rate limited by YouTube, wait a few minutes")
        die(EXIT_FETCH, f"fetch failed: {err.splitlines()[-1] if err else 'no output from yt-dlp'}")
    return json.loads(proc.stdout)


def pick_track(meta: dict, workdir: Path):
    """Prefer human-written subs, fall back to auto-generated."""
    manual = set(meta.get("subtitles") or {})
    for lang in (meta.get("requested_subtitles") or {}):
        path = workdir / f"{meta['id']}.{lang}.json3"
        if path.exists():
            return path, ("manual" if lang in manual else "auto")
    return None, None


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


def already_ingested(video_id: str):
    for path in CONTENT_DIR.rglob("*.md"):
        if f"video_id: {video_id}" in path.read_text(encoding="utf-8"):
            return path
    return None


def render(meta: dict, sections: list, source: str) -> str:
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
        f'title: "{title.replace(chr(34), chr(39))}"',
        f'channel: "{channel.replace(chr(34), chr(39))}"',
        f"url: {url}",
        f"video_id: {vid}",
        f"upload_date: {date}",
        f"duration: {meta.get('duration') or 0}",
        f"transcript_source: {source}",
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

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        meta = fetch(args.url, workdir)

        existing = already_ingested(meta["id"])
        if existing and not args.force:
            print(f"already ingested: {existing}", file=sys.stderr)
            print(existing)
            return

        track, source = pick_track(meta, workdir)
        if track is None:
            die(EXIT_NO_TRANSCRIPT, f"no English transcript available for {meta['id']}")

        words = to_words(json.loads(track.read_text(encoding="utf-8")).get("events", []))
        if not words:
            die(EXIT_NO_TRANSCRIPT, f"transcript for {meta['id']} was empty")
        sections = to_sections(words, meta.get("chapters"))

        raw_date = meta.get("upload_date") or ""
        date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}" if raw_date else "undated"
        out = CONTENT_DIR / slugify(meta.get("channel") or meta.get("uploader") or "", meta["id"])
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{date}-{slugify(meta.get('title') or '', meta['id'])}.md"
        path.write_text(render(meta, sections, source), encoding="utf-8")

    print(path)


if __name__ == "__main__":
    main()
