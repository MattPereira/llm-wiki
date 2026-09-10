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

export function nameFor(
  table: Map<string, string>,
  slug: string,
  file: string,
): string {
  const name = table.get(slug);
  if (name === undefined) throw new Error(`${file} defines no "${slug}"`);
  return name;
}
