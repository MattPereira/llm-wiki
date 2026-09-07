"""Creator folder resolution shared by the ingest scripts. See ADR-0006."""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "wiki" / "raw"
CREATORS = ROOT / "creators.toml"


def resolve(platform: str, derived: str) -> str:
    """Canonical creator folder for a platform-derived slug.

    Falls back to the derived slug and warns: adding a creator is the most frequent
    operation, so an unmapped one must not block an ingest. See ADR-0006.
    """
    table = tomllib.loads(CREATORS.read_text(encoding="utf-8"))
    for canonical, entry in table.items():
        if derived in entry.get(platform, []):
            return canonical
    print(
        f"warning: {platform} slug '{derived}' is not in creators.toml; writing to "
        f"wiki/raw/{derived}/. Add it and `git mv` if this creator already has a folder.",
        file=sys.stderr,
    )
    return derived


def target(creator: str, filename: str, marker: str) -> Path:
    """Path to write, refusing to clobber a different item's file.

    Merging platforms into one folder makes a same-day, same-slug collision possible
    between a video and a post. `marker` is the frontmatter id line of the incoming
    item; a file already carrying it is the same item being re-ingested with --force.
    """
    path = RAW_DIR / creator / filename
    if path.exists() and marker not in path.read_text(encoding="utf-8"):
        print(f"refusing to overwrite {path} ({marker} not in it)", file=sys.stderr)
        sys.exit(1)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
