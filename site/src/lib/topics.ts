import { z } from "astro/zod";
import { nameFor, parseNamedTables } from "./vocabulary.js";
// Symlink to the repo root, imported for the same reason as creators.toml.
import toml from "../topics.toml?raw";

const FILE = "topics.toml";

export const parseTopics = (toml: string): Map<string, string> =>
  parseNamedTables(toml, FILE);

const topics = parseTopics(toml);

export const topicName = (slug: string): string => nameFor(topics, slug, FILE);

const isTopic = (slug: string): boolean => topics.has(slug);

export const topicSlugs = (): string[] => [...topics.keys()];

/**
 * The vocabulary is a closed set, so a typo must fail the build rather than
 * silently create an orphan Topic page nothing else links to.
 */
export const topicSlug = z.string().superRefine((slug, ctx) => {
  if (isTopic(slug)) return;
  ctx.addIssue({
    code: "custom",
    message: `"${slug}" is not in ${FILE} (have: ${topicSlugs().join(", ")})`,
  });
});
