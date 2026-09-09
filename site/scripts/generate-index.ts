/**
 * Regenerates `wiki/index.md` from Summary frontmatter. Run by the summarize
 * skill at the end of a run; the Index is a derived artifact, never hand-edited.
 */
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { load } from "js-yaml";
import { renderIndex, type IndexedSummary } from "../src/lib/index-markdown.js";
import { summarySchema } from "../src/lib/summary-schema.js";

const REPO = resolve(fileURLToPath(import.meta.url), "../../..");
const SUMMARIES = join(REPO, "wiki/summaries");
const INDEX = join(REPO, "wiki/index.md");

const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---/;

/** js-yaml, same parser and version as the Astro loader, so a bare `2026-09-05`
 * reaches the schema as a Date on both paths rather than as a string on one. */
function frontmatterOf(file: string): unknown {
  const match = FRONTMATTER.exec(readFileSync(file, "utf8"));
  if (!match) throw new Error(`${relative(REPO, file)}: no frontmatter`);
  return load(match[1]!);
}

function read(file: string): IndexedSummary {
  const parsed = summarySchema.safeParse(frontmatterOf(file));
  if (!parsed.success) {
    const issues = parsed.error.issues
      .map((issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`)
      .join("; ");
    throw new Error(`${relative(REPO, file)}: ${issues}`);
  }
  return { id: relative(SUMMARIES, file).replace(/\.md$/, ""), data: parsed.data };
}

const files = readdirSync(SUMMARIES, { recursive: true, encoding: "utf8" })
  .filter((entry) => entry.endsWith(".md"))
  .map((entry) => join(SUMMARIES, entry))
  .sort();

writeFileSync(INDEX, renderIndex(files.map(read)));
console.log(`wiki/index.md: ${files.length} summaries`);
