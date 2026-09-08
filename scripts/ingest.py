#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Route a content URL to its platform-specific ingestion script.

Usage:  uv run scripts/ingest.py <url> [--force]
"""

import argparse
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


SCRIPT_DIR = Path(__file__).resolve().parent


def handler_for(url: str) -> Path:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"not an HTTP(S) URL: {url}")

    host = parsed.hostname.lower().rstrip(".")
    if host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com"):
        return SCRIPT_DIR / "ingest_youtube.py"
    if host == "substack.com" or host.endswith(".substack.com"):
        return SCRIPT_DIR / "ingest_substack.py"
    raise ValueError(f"unsupported URL host: {host}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a URL to the appropriate ingestion script.")
    parser.add_argument("url")
    parser.add_argument("--force", action="store_true", help="re-ingest even if already present")
    args = parser.parse_args()

    try:
        script = handler_for(args.url)
    except ValueError as error:
        parser.error(str(error))

    command = ["uv", "run", str(script), args.url]
    if args.force:
        command.append("--force")
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
