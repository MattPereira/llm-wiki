import { z } from "astro/zod";
import { topicSlug } from "./topics.js";

// Strict on purpose: a Summary missing a field fails the build by name, which is
// how the summarize skill finds out it forgot one. See docs/adr/0001.
//
// No `creator` field: the Creator is the folder the Summary sits in, and the
// display name comes from creators.toml. A name in frontmatter would be a second
// copy nothing validates, free to drift from the one every consumer renders.
//
// Lives here rather than in content.config.ts so the Index generator validates
// frontmatter against the same definition the site build does.
export const summarySchema = z.object({
  type: z.literal("summary"),
  title: z.string(),
  source: z.string(),
  url: z.string().url(),
  upload_date: z.date(),
  blurb: z.string(),
  topics: z.array(topicSlug).nonempty(),
});

export type SummaryFrontmatter = z.infer<typeof summarySchema>;
