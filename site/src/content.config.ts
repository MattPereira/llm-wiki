import { glob } from "astro/loaders";
import { defineCollection } from "astro:content";
import { summarySchema } from "./lib/summary-schema.js";

const summaries = defineCollection({
  // src/wiki-summaries is a symlink to ../wiki/summaries. Vite only watches the
  // project root (site/), so pointing the loader straight at ../wiki/summaries
  // loads the entries but never hot-reloads them — an ingest run needs a server
  // restart to show up. Reaching them through an in-root symlink keeps
  // add/change/delete live in dev; ids (and so URLs) are unchanged.
  loader: glob({ pattern: "**/*.md", base: "./src/wiki-summaries" }),
  schema: summarySchema,
});

export const collections = { summaries };
