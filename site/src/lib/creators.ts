import { loadNamedTables, nameFor, parseNamedTables } from "./vocabulary.js";

const FILE = "creators.toml";

export const parseCreators = (toml: string): Map<string, string> =>
  parseNamedTables(toml, FILE);

const creators = loadNamedTables(FILE);

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
