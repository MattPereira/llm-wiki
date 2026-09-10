import { creatorName } from "./creators.js";
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

/** Links are resolved from `wiki/index.md`, and the id mirrors the file tree. */
const entry = (summary: IndexedSummary): string =>
  `- [${summary.data.title}](summaries/${summary.id}.md) — ${isoDate(summary.data.upload_date)} · ${creatorName(creatorSlug(summary.id))} — ${summary.data.blurb}`;

/**
 * Pure: filesystem reads and the write to `wiki/index.md` live in the generator
 * script, so the shape of the Index is testable from fixture frontmatter alone.
 */
export const renderIndex = (summaries: readonly IndexedSummary[]): string => {
  const sections = [...byCreator(summaries)]
    .map(([slug, entries]) => ({ name: creatorName(slug), entries }))
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(({ name, entries }) => `## ${name}\n\n${entries.map(entry).join("\n")}\n`);

  return ["# Index\n", ...sections].join("\n");
};
