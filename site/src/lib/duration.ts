import { readFileSync } from "node:fs";

/**
 * Duration is not part of the Summary frontmatter contract — it belongs to the
 * Source, so it lives on the Raw, which the Site reads at build time but never
 * publishes. Absent for Substack posts, which have no duration at all.
 */
export function readDurationSeconds(rawPath: string): number | undefined {
  let raw: string;
  try {
    raw = readFileSync(rawPath, "utf8");
  } catch {
    return undefined;
  }

  const frontmatter = raw.split("---")[1];
  const seconds = Number(frontmatter?.match(/^duration:\s*(\d+)$/m)?.[1]);

  return Number.isFinite(seconds) && seconds > 0 ? seconds : undefined;
}

export function formatDuration(seconds: number): string {
  const parts = [
    Math.floor(seconds / 3600),
    Math.floor(seconds / 60) % 60,
    seconds % 60,
  ].slice(seconds < 3600 ? 1 : 0);

  return parts
    .map((part, i) => (i === 0 ? String(part) : String(part).padStart(2, "0")))
    .join(":");
}
