import { describe, expect, it } from "vitest";
import { byCreator, byTopic, creatorSlug, newestFirst } from "./summaries.js";

const summary = (id: string, date: string, topics: string[]) => ({
  id,
  data: { upload_date: new Date(date), topics },
});

const kyla = summary("kyla-scanlon/2026-09-05-ai-agents", "2026-09-05", ["ai"]);
const taiki = summary("taiki-maeda/2026-07-15-bottoming", "2026-07-15", [
  "crypto-markets",
]);
const thousand = summary("1000x/2026-09-04-market-update", "2026-09-04", [
  "crypto-markets",
  "ai",
]);

describe("creatorSlug", () => {
  it("takes the folder segment, not the file segment", () => {
    expect(creatorSlug("kyla-scanlon/2026-09-05-ai-agents")).toBe(
      "kyla-scanlon",
    );
  });
});

describe("newestFirst", () => {
  it("sorts by upload date descending", () => {
    expect(newestFirst([taiki, kyla, thousand]).map((s) => s.id)).toEqual([
      kyla.id,
      thousand.id,
      taiki.id,
    ]);
  });

  it("leaves the input array alone", () => {
    const input = [taiki, kyla];
    newestFirst(input);
    expect(input[0]).toBe(taiki);
  });
});

describe("byCreator", () => {
  it("groups by creator slug, newest first within each creator", () => {
    const older = summary("kyla-scanlon/2026-01-01-old", "2026-01-01", ["ai"]);
    const grouped = byCreator([older, taiki, kyla]);

    expect(grouped.get("kyla-scanlon")?.map((s) => s.id)).toEqual([
      kyla.id,
      older.id,
    ]);
    expect(grouped.get("taiki-maeda")?.map((s) => s.id)).toEqual([taiki.id]);
  });
});

describe("byTopic", () => {
  it("collects a topic across creators, newest first", () => {
    const grouped = byTopic([taiki, kyla, thousand]);

    expect(grouped.get("crypto-markets")?.map((s) => s.id)).toEqual([
      thousand.id,
      taiki.id,
    ]);
  });

  it("files a summary under every topic it carries", () => {
    expect(byTopic([thousand]).get("ai")?.map((s) => s.id)).toEqual([
      thousand.id,
    ]);
  });

  it("omits a topic no summary carries, so callers decide what empty looks like", () => {
    expect(byTopic([kyla]).has("macro")).toBe(false);
  });
});
