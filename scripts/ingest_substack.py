#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4==4.15.0"]
# ///
"""Fetch a Substack post and write it as Markdown into content/substack/.

Usage:  uv run scripts/ingest_substack.py <url> [--force]
Prints the written path on stdout. Everything else goes to stderr.

Exit codes: 0 ok (or already ingested), 1 fetch failed, 2 paywalled.

Unlike the YouTube transcript, a Substack post arrives already structured -- the
author wrote the headings and the paragraphs -- so there is no agent step after
this script. What it writes is what the wiki keeps.
"""

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "substack"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
WARN_WORDS = 20  # an ignored element holding more than this is probably content, not chrome

EXIT_FETCH, EXIT_PAYWALLED = 1, 2

# Dropped whole, before anything is converted: Substack interleaves subscribe forms,
# polls and share buttons among the paragraphs, and their captions are real <p> tags.
DROP_TAGS = {"form", "button", "svg", "script", "style", "input", "select", "textarea"}
# Exact class tokens, not substrings: `footnote` is the note block at the end of the
# post, while `footnote-anchor` is the inline marker that has to survive in the prose.
DROP_CLASSES = {"poll-embed", "button-wrapper", "native-audio-embed",
                "digest-post-embed", "footnote"}
DROP_CLASS_PREFIXES = ("subscription-widget-wrap",)

BLOCKS = {"p", "h2", "h3", "h4", "ul", "ol", "blockquote", "hr", "figure"}
HEADINGS = {"h2": "##", "h3": "###", "h4": "####"}


def die(code: int, msg: str):
    print(msg, file=sys.stderr)
    sys.exit(code)


def slugify(text: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")[:80].strip("-")
    return slug or fallback


def get(url: str) -> tuple[str, bytes]:
    """Fetch following redirects; returns the final URL and the body."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as resp:
            return resp.geturl(), resp.read()
    except urllib.error.HTTPError as e:
        die(EXIT_FETCH, f"fetch failed: HTTP {e.code} for {url}")
    except (urllib.error.URLError, TimeoutError) as e:
        die(EXIT_FETCH, f"fetch failed: {e} for {url}")


def resolve(url: str) -> tuple[str, str]:
    """Follow the share URL to its canonical home.

    substack.com/home/post/p-<id> and substack.com/@user/p-<id> are both redirects
    to <publication>/p/<slug>, and only the latter shape has a JSON API.
    """
    final, _ = get(url)
    match = re.match(r"(https?://[^/]+)/p/([^/?#]+)", final)
    if not match:
        die(EXIT_FETCH, f"not a Substack post URL: resolved to {final}")
    return match.group(1), match.group(2)


def fetch_post(host: str, slug: str) -> dict:
    _, body = get(f"{host}/api/v1/posts/{slug}")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        die(EXIT_FETCH, f"unexpected response from {host}/api/v1/posts/{slug}")


def dropped(el) -> bool:
    if el.name in DROP_TAGS:
        return True
    classes = el.get("class") or []
    return any(c in DROP_CLASSES or c.startswith(DROP_CLASS_PREFIXES) for c in classes)


def inline(node) -> str:
    """Render an element's children as Markdown inline text."""
    out = []
    for child in node.children:
        if isinstance(child, NavigableString):
            out.append(str(child))
            continue
        if dropped(child):
            continue
        text = inline(child)
        if child.name in ("strong", "b"):
            out.append(f"**{text}**" if text.strip() else text)
        elif child.name in ("em", "i"):
            out.append(f"*{text}*" if text.strip() else text)
        elif child.name == "a":
            classes = " ".join(child.get("class") or [])
            if "footnote-anchor" in classes:
                out.append(f"[{text}]")  # literal marker; the note itself lands under ## Footnotes
            else:
                href = child.get("href", "")
                out.append(f"[{text}]({href})" if href else text)
        elif child.name == "br":
            out.append("\n")
        else:
            out.append(text)
    return re.sub(r"[ \t]+", " ", "".join(out)).strip()


def image(container) -> str | None:
    """A captioned-image-container carries the CDN url twice: the <a> wrapper has the
    full-size original, the <img> a resized one. Prefer the original."""
    link = container.find("a", class_="image-link")
    img = container.find("img")
    src = (link.get("href") if link else None) or (img.get("src") if img else None)
    if not src:
        return None
    caption = container.find("figcaption")
    block = f"![]({src})"
    if caption and caption.get_text(strip=True):
        block += "\n\n" + inline(caption)
    return block


def block(el, warn) -> str | None:
    classes = " ".join(el.get("class") or [])

    if "captioned-image-container" in classes or el.name == "figure":
        return image(el)
    if "datawrapper-wrap" in classes:
        frame = el.find("iframe")
        src = frame.get("src") if frame else ""
        return f"[chart: {src}]" if src else None
    if el.name == "hr" or (el.name == "div" and el.find("hr") and not el.get_text(strip=True)):
        return "---"
    if el.name in HEADINGS:
        text = inline(el)
        return f"{HEADINGS[el.name]} {text}" if text else None
    if el.name == "p":
        text = inline(el)
        return text or None
    if el.name == "blockquote":
        parts = [p for p in (block(c, warn) for c in el.find_all(["p", "h3", "h4"], recursive=False)) if p]
        text = "\n\n".join(parts) or inline(el)
        return "\n".join("> " + line if line else ">" for line in text.split("\n")) or None
    if el.name in ("ul", "ol"):
        items = []
        for i, li in enumerate(el.find_all("li", recursive=False), start=1):
            text = inline(li)
            if text:
                items.append(f"{i}. {text}" if el.name == "ol" else f"- {text}")
        return "\n".join(items) or None

    warn(el)
    return None


def convert(body_html: str) -> tuple[list[str], list[str]]:
    """Returns (blocks, footnotes). Anything neither converted nor explicitly dropped
    is ignored -- a new Substack widget vanishes rather than leaking in as prose, and
    the stderr warning is how you find out it happened."""
    soup = BeautifulSoup(body_html, "html.parser")

    footnotes = []
    for note in soup.find_all("div", class_="footnote"):
        number = note.find("a", class_="footnote-number")
        content = note.find("div", class_="footnote-content")
        if content:
            footnotes.append(f"[{number.get_text(strip=True) if number else len(footnotes) + 1}] {inline(content)}")

    def warn(el):
        text = el.get_text(" ", strip=True)
        if len(text.split()) > WARN_WORDS:
            print(f"warning: ignored <{el.name} class={' '.join(el.get('class') or []) or '-'}> "
                  f"holding {len(text.split())} words: {text[:80]}...", file=sys.stderr)

    blocks = []
    for el in soup.children:
        if isinstance(el, NavigableString):
            if el.strip():
                blocks.append(str(el).strip())
            continue
        if dropped(el):
            continue
        rendered = block(el, warn) if (el.name in BLOCKS or el.name == "div") else None
        if rendered is None and el.name not in BLOCKS and el.name != "div":
            warn(el)
        if rendered and not (rendered == "---" and blocks[-1:] == ["---"]):
            blocks.append(rendered)  # Substack stacks dividers for visual weight; one is enough
    return blocks, footnotes


def publication(post: dict, host: str) -> tuple[str, str]:
    """Returns (display name, directory slug).

    The by-slug endpoint carries only publication_id; the publication itself is
    reachable through the bylines. Its subdomain is the stable directory key --
    the display name is free text, and custom domains (semianalysis) don't match it.
    """
    fallback = host.split("//")[-1].split(".")[0]
    for byline in post.get("publishedBylines") or []:
        for membership in byline.get("publicationUsers") or []:
            pub = membership.get("publication") or {}
            if pub.get("id") == post.get("publication_id"):
                return pub.get("name") or fallback, pub.get("subdomain") or fallback
    return fallback, fallback


def already_ingested(post_id):
    for path in CONTENT_DIR.rglob("*.md"):
        if f"post_id: {post_id}" in path.read_text(encoding="utf-8"):
            return path
    return None


def render(post: dict, blocks: list[str], footnotes: list[str], publication: str) -> str:
    q = lambda s: (s or "").replace('"', "'")
    title = post.get("title") or post.get("slug") or ""
    subtitle = post.get("subtitle") or ""
    author = ", ".join(b.get("name", "") for b in (post.get("publishedBylines") or []) if b.get("name"))
    url = post.get("canonical_url") or ""
    date = (post.get("post_date") or "")[:10]
    words = sum(len(b.split()) for b in blocks)

    lines = [
        "---",
        f'title: "{q(title)}"',
        f'subtitle: "{q(subtitle)}"',
        f'publication: "{q(publication)}"',
        f'author: "{q(author)}"',
        f"url: {url}",
        f"post_id: {post.get('id')}",
        f"post_date: {date}",
        f"fetched_at: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"word_count: {words}",
        f"footnotes: {len(footnotes)}",
        "---",
        "",
        f"# {title}",
        "",
    ]
    if subtitle:
        lines += [f"*{subtitle}*", ""]
    lines += [f"**{publication}** · {date} · [read]({url})", ""]
    for b in blocks:
        lines += [b, ""]
    if footnotes:
        lines += ["## Footnotes", ""]
        for note in footnotes:
            lines += [note, ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ingest a Substack post as Markdown.")
    parser.add_argument("url")
    parser.add_argument("--force", action="store_true", help="re-ingest even if already present")
    args = parser.parse_args()

    host, slug = resolve(args.url)
    post = fetch_post(host, slug)

    audience = post.get("audience")
    if audience != "everyone":
        # The API answers 200 for paid posts but the body stops partway with no marker
        # in it. A half-post is worse than no post: nothing downstream can tell.
        die(EXIT_PAYWALLED, f"paywalled ({audience}), skipped: {post.get('canonical_url') or args.url}")

    existing = already_ingested(post.get("id"))
    if existing and not args.force:
        print(f"already ingested: {existing}", file=sys.stderr)
        print(existing)
        return

    blocks, footnotes = convert(post.get("body_html") or "")
    if not blocks:
        die(EXIT_FETCH, f"no body content in {post.get('canonical_url') or args.url}")

    name, pub_slug = publication(post, host)
    out = CONTENT_DIR / pub_slug
    out.mkdir(parents=True, exist_ok=True)
    date = (post.get("post_date") or "")[:10] or "undated"
    path = out / f"{date}-{slugify(post.get('slug') or '', str(post.get('id')))}.md"
    path.write_text(render(post, blocks, footnotes, name), encoding="utf-8")

    print(path)


if __name__ == "__main__":
    main()
