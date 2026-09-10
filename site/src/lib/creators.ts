import { nameFor, parseNamedTables } from "./vocabulary.js";
// src/creators.toml is a symlink to the repo root. Imported rather than read
// with fs so Vite tracks it as a module dep and dev picks up a new Creator
// without a restart.
import toml from "../creators.toml?raw";

const FILE = "creators.toml";

export const parseCreators = (toml: string): Map<string, string> =>
  parseNamedTables(toml, FILE);

const creators = parseCreators(toml);

/**
 * Throws rather than falling back to the slug: a slug leaking into a page is the
 * exact thing creators.toml exists to prevent, and a Summary under an unmapped
 * folder is a reconciliation the ingest scripts already warn about.
 */
export const creatorName = (slug: string): string =>
  nameFor(creators, slug, FILE);

export const creatorSlugs = (): string[] => [...creators.keys()];

/**
 * A Creator lives at `/<slug>/`, a top-level dynamic route, so a slug matching one
 * of the site's own pages would be shadowed by it and the Creator page would just
 * vanish with no build error. Cheaper to refuse the slug than to debug the gap.
 */
export const RESERVED_SLUGS = ["creators", "topics", "search"];

export function assertRoutableCreators(slugs: readonly string[] = creatorSlugs()) {
  for (const slug of slugs) {
    if (RESERVED_SLUGS.includes(slug)) {
      throw new Error(
        `${FILE}: [${slug}] collides with the /${slug} page; rename the Creator`,
      );
    }
  }
}
