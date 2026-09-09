/** The slice of a Summary the listing helpers need — narrower than a full
 * collection entry so they stay testable without the content layer. */
export interface ListedSummary {
  id: string;
  data: { upload_date: Date; topics: readonly string[] };
}

/** Permalinks mirror the file tree, so the id's first segment is the Creator. */
export const creatorSlug = (id: string): string => id.split("/")[0]!;

export const newestFirst = <T extends ListedSummary>(summaries: readonly T[]): T[] =>
  [...summaries].sort(
    (a, b) => b.data.upload_date.valueOf() - a.data.upload_date.valueOf(),
  );

const groupBy = <T extends ListedSummary>(
  summaries: readonly T[],
  keysOf: (summary: T) => readonly string[],
): Map<string, T[]> => {
  const grouped = new Map<string, T[]>();

  for (const summary of newestFirst(summaries)) {
    for (const key of keysOf(summary)) {
      const bucket = grouped.get(key);
      if (bucket) bucket.push(summary);
      else grouped.set(key, [summary]);
    }
  }

  return grouped;
};

export const byCreator = <T extends ListedSummary>(
  summaries: readonly T[],
): Map<string, T[]> => groupBy(summaries, (s) => [creatorSlug(s.id)]);

export const byTopic = <T extends ListedSummary>(
  summaries: readonly T[],
): Map<string, T[]> => groupBy(summaries, (s) => s.data.topics);
