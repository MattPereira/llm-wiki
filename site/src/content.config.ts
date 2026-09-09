import { glob } from "astro/loaders";
import { defineCollection } from "astro:content";
import { summarySchema } from "./lib/summary-schema.js";

const summaries = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "../wiki/summaries" }),
  schema: summarySchema,
});

export const collections = { summaries };
