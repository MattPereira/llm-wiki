import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { parse } from "smol-toml";

/** Both vocabulary files are tables-of-tables keyed by slug, each carrying a `name`. */
export function parseNamedTables(toml: string, file: string): Map<string, string> {
  const entries = Object.entries(parse(toml));

  return new Map(
    entries.map(([slug, table]) => {
      const name = (table as { name?: unknown })?.name;
      if (typeof name !== "string" || name === "") {
        throw new Error(`${file}: [${slug}] has no "name"`);
      }
      return [slug, name];
    }),
  );
}

/**
 * Walks up from the cwd rather than resolving against `import.meta.url`: Astro
 * bundles this module into `dist/.prerender/chunks/`, so a module-relative path
 * points somewhere that does not exist by the time the static routes render.
 */
function repoFile(file: string): string {
  let dir = resolve(process.cwd());

  for (;;) {
    const candidate = join(dir, file);
    if (existsSync(candidate)) return candidate;

    const parent = dirname(dir);
    if (parent === dir) throw new Error(`${file} not found above ${process.cwd()}`);
    dir = parent;
  }
}

export function loadNamedTables(file: string): Map<string, string> {
  return parseNamedTables(readFileSync(repoFile(file), "utf8"), file);
}

export function nameFor(
  table: Map<string, string>,
  slug: string,
  file: string,
): string {
  const name = table.get(slug);
  if (name === undefined) throw new Error(`${file} defines no "${slug}"`);
  return name;
}
