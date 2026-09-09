import { glob } from "astro/loaders";
import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { topicSlug } from "./lib/topics.js";

// Strict on purpose: a Summary missing a field fails the build by name, which is
// how the summarize skill finds out it forgot one. See docs/adr/0001.
const summaries = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "../wiki/summaries" }),
  schema: z.object({
    type: z.literal("summary"),
    title: z.string(),
    creator: z.string(),
    source: z.string(),
    url: z.string().url(),
    upload_date: z.date(),
    blurb: z.string(),
    topics: z.array(topicSlug).nonempty(),
  }),
});

export const collections = { summaries };
