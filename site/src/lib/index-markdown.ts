import { byCreator, creatorSlug, type ListedSummary } from "./summaries.js";

/** The slice of a Summary the Index renders. */
export interface IndexedSummary extends ListedSummary {
  data: {
    upload_date: Date;
    topics: readonly string[];
    title: string;
    blurb: string;
  };
}

/** Frontmatter dates are date-only; ISO in UTC or they render a day early. */
const isoDate = (date: Date): string => date.toISOString().slice(0, 10);

/** Resolves a Creator slug to its display name. */
export type NameOf = (slug: string) => string;

/** Links are resolved from `wiki/index.md`, and the id mirrors the file tree. */
const entry = (summary: IndexedSummary, creatorName: NameOf): string =>
  `- [${summary.data.title}](summaries/${summary.id}.md) — ${isoDate(summary.data.upload_date)} · ${creatorName(creatorSlug(summary.id))} — ${summary.data.blurb}`;

/**
 * Pure: the name lookup is injected and the write to `wiki/index.md` lives in the
 * generator script, so the shape of the Index is testable from fixtures alone,
 * and the script stays runnable under plain Node.
 */
export const renderIndex = (
  summaries: readonly IndexedSummary[],
  creatorName: NameOf,
): string => {
  const sections = [...byCreator(summaries)]
    .map(([slug, entries]) => ({ name: creatorName(slug), entries }))
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(({ name, entries }) => `## ${name}\n\n${entries.map((e) => entry(e, creatorName)).join("\n")}\n`);

  return ["# Index\n", ...sections].join("\n");
};
