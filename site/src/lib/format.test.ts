import { describe, expect, it } from "vitest";
import { formatDate, permalink, sourceLabel, summaryCount } from "./format.js";

describe("summaryCount", () => {
  it("singularises one", () => {
    expect(summaryCount(1)).toBe("1 summary");
  });

  it("pluralises everything else, zero included", () => {
    expect(summaryCount(0)).toBe("0 summaries");
    expect(summaryCount(4)).toBe("4 summaries");
  });
});

describe("formatDate", () => {
  it("formats a date-only frontmatter value in UTC, not a day early", () => {
    expect(formatDate(new Date("2026-09-05"))).toBe("September 5, 2026");
  });
});

describe("permalink", () => {
  it("mirrors the file tree", () => {
    expect(permalink("kyla-scanlon/2026-09-05-ai-agents")).toBe(
      "/kyla-scanlon/2026-09-05-ai-agents/",
    );
  });
});

describe("sourceLabel", () => {
  it("says watch for video", () => {
    expect(sourceLabel("https://www.youtube.com/watch?v=abc")).toBe(
      "Watch the original",
    );
  });

  it("says read for anything else", () => {
    expect(sourceLabel("https://kyla.substack.com/p/x")).toBe(
      "Read the original",
    );
  });
});
