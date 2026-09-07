#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pull recent items for every creator in creators.toml into wiki/raw/.

Usage:  uv run scripts/backfill.py [--since YYYY-MM-DD] [--limit N] [--dry-run] [creator ...]

Listing a channel or publication is one cheap request that names many items; fetching
an item is expensive and, on YouTube, rate-limited. So this lists first, decides what
it wants, and only then fetches -- and --dry-run stops after deciding.

The ingest scripts remain the only things that write wiki/raw/. This drives them as
subprocesses so their exit codes stay the whole interface, which is also what makes a
re-run safe: both detect an already-ingested item and exit 0 without refetching.
"""

import argparse
import json
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREATORS = ROOT / "creators.toml"
FEED = "https://www.youtube.com/feeds/videos.xml?"

SINCE = "2026-08-01"
LIMIT = 5  # newest N per creator inside the window; the floor alone is unbounded,
# and a daily publisher would otherwise crowd out everyone else
SLEEP_YT = 10  # seconds between YouTube fetches
SLEEP_SUB = 3  # Substack is a plain JSON API and needs only token politeness

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

OK, RATE_LIMITED = 0, 3  # ingest_youtube.py exit codes worth reacting to


class RateLimited(Exception):
    """YouTube throttled us. Abort everything: the next creator hits the same wall."""


def log(msg: str):
    print(msg, file=sys.stderr)


def get(url: str) -> bytes | None:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=30) as resp:
            return resp.read()
    except (urllib.error.URLError, TimeoutError) as e:
        log(f"  ! could not list {url}: {e}")
        return None


def youtube_listing(channel: str, since: str, limit: int, long_form_only: bool = False) -> list[tuple[str, str]]:
    """(video_id, title) for uploads on or after `since`, newest-first.

    `long_form_only` reads the auto-generated long-form uploads playlist (channel `UC...`
    becomes playlist `UULF...`) instead of the channel itself. That is YouTube's own
    shorts/long-form split rather than a guess at one, and it costs nothing extra: same
    endpoint, same single request. It also stretches the 15-entry ceiling a long way for
    a channel that posts clips, since clips no longer occupy slots. Opt-in per creator --
    a creator whose shorts are worth reading should not set it.

    Read from the channel RSS feed, not from a yt-dlp channel listing. The feed is one
    unauthenticated request, is genuinely newest-first, carries <published> dates, and
    includes shorts -- whereas a flat yt-dlp listing has no date field at all and the
    /videos tab returns neither shorts nor a reliable chronological order. Without
    dates here every candidate would cost a real fetch just to be rejected, which is
    the rate-limit exposure this whole script exists to avoid.

    The feed holds only the 15 newest uploads. That is the ceiling on how far back a
    run can reach; a `since` older than those 15 silently gets whatever they are.
    """
    cid = channel.rstrip("/").rsplit("/", 1)[-1]
    body = get(FEED + (f"playlist_id=UULF{cid[2:]}" if long_form_only else f"channel_id={cid}"))
    if body is None and long_form_only:
        # Not every channel has the derived playlist; a silent empty list would look
        # like "nothing new" rather than "could not ask".
        log(f"  ! no long-form playlist for {cid}; falling back to the full channel feed")
        body = get(FEED + f"channel_id={cid}")
    if body is None:
        return []

    items = []
    for entry in re.findall(r"<entry>(.*?)</entry>", body.decode("utf-8"), re.S):
        found = [re.search(p, entry, re.S) for p in
                 (r"<yt:videoId>(.*?)</yt:videoId>", r"<published>(.*?)</published>", r"<title>(.*?)</title>")]
        if not all(found):
            continue
        vid, published, title = (m.group(1) for m in found)
        if published[:10] >= since:
            items.append((vid, title))
        if len(items) == limit:
            break
    return items


def substack_listing(host: str, since: str, limit: int) -> list[tuple[str, str]]:
    """(url, title) for free posts on or after `since`, newest-first.

    The archive endpoint carries post_date and audience, so unlike YouTube both the
    date floor and the paywall filter apply before a single post is fetched. Paid posts
    are dropped here rather than fetched and rejected: the API answers 200 with a
    truncated preview, which is why ingest_substack.py refuses them at all.
    """
    body = get(f"{host}/api/v1/archive?sort=new&limit={max(limit * 4, 20)}")
    if body is None:
        return []
    try:
        posts = json.loads(body)
    except json.JSONDecodeError:
        log(f"  ! unexpected archive response from {host}")
        return []

    chosen = []
    for post in posts:
        if len(chosen) == limit:
            break
        date = (post.get("post_date") or "")[:10]
        if not date or date < since:
            continue  # newest-first, but keep scanning: drafts and pins can sort oddly
        if post.get("audience") != "everyone":
            log(f"  - skipped (paid): {post.get('title') or post.get('slug')}")
            continue
        link = post.get("canonical_url") or f"{host}/p/{post.get('slug')}"
        chosen.append((link, post.get("title") or post.get("slug") or link))
    return chosen


def ingest(script: str, url: str) -> bool:
    """True only when a new file landed.

    Both scripts exit 0 for an item already in wiki/raw/ and say so on stderr, so the
    exit code alone cannot tell a fetch from a skip.
    """
    proc = subprocess.run(["uv", "run", str(ROOT / "scripts" / script), url],
                          capture_output=True, text=True, cwd=ROOT)
    if proc.returncode == RATE_LIMITED and script == "ingest_youtube.py":
        raise RateLimited(url)
    skipped = "already ingested" in proc.stderr
    note = (proc.stdout.strip().splitlines() or proc.stderr.strip().splitlines() or ["?"])[-1]
    log(f"  {'+' if proc.returncode == OK and not skipped else '-'} {note}")
    return proc.returncode == OK and not skipped


def main():
    parser = argparse.ArgumentParser(description="Backfill recent creator content into wiki/raw/.")
    parser.add_argument("creators", nargs="*", help="creator slugs; default every creator with a source")
    parser.add_argument("--since", default=SINCE, metavar="YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=LIMIT, help="newest items per creator")
    parser.add_argument("--dry-run", action="store_true", help="list what would be fetched, fetch nothing")
    args = parser.parse_args()

    table = tomllib.loads(CREATORS.read_text(encoding="utf-8"))
    wanted = args.creators or list(table)
    for unknown in [c for c in wanted if c not in table]:
        log(f"unknown creator: {unknown}")
        return 1

    fetched, pending = 0, []
    try:
        for slug in wanted:
            entry = table[slug]
            if not (entry.get("channel") or entry.get("host")):
                continue
            log(f"\n{slug}")

            if entry.get("host"):
                for url, title in substack_listing(entry["host"], args.since, args.limit):
                    if args.dry_run:
                        log(f"  ? {title}")
                        continue
                    fetched += ingest("ingest_substack.py", url)
                    time.sleep(SLEEP_SUB)

            if entry.get("channel"):
                for vid, title in youtube_listing(entry["channel"], args.since, args.limit,
                                                  entry.get("long_form_only", False)):
                    url = f"https://www.youtube.com/watch?v={vid}"
                    if args.dry_run:
                        log(f"  ? {title}  ({url})")
                        continue
                    landed = ingest("ingest_youtube.py", url)
                    fetched += landed
                    if landed:
                        time.sleep(SLEEP_YT)  # a skip made no request; nothing to pace
    except RateLimited as e:
        pending = wanted[wanted.index(slug):]
        log(f"\nrate limited on {e}; stopping.")
        log(f"wait a few minutes, then: uv run scripts/backfill.py {' '.join(pending)}")

    if not args.dry_run:
        log(f"\ningested {fetched} new file(s).")
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
