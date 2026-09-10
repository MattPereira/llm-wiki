import { describe, expect, it } from "vitest";
import { creatorName } from "./creators.js";
import { renderIndex } from "./index-markdown.js";

const summary = (id: string, date: string, title: string, blurb: string) => ({
  id,
  data: { upload_date: new Date(date), topics: ["ai"], title, blurb },
});

const kyla = summary(
  "kyla-scanlon/2026-09-05-ai-agents",
  "2026-09-05",
  "AI Agents",
  "Agents edited a wiki into an answer key.",
);
const kylaOlder = summary(
  "kyla-scanlon/2026-01-01-old",
  "2026-01-01",
  "Older Post",
  "An older take.",
);
const taiki = summary(
  "taiki-maeda/2026-07-15-bottoming",
  "2026-07-15",
  "Crypto is Bottoming",
  "Maeda favors gradual accumulation.",
);

describe("renderIndex", () => {
  it("groups entries under a heading per Creator, ordered by display name", () => {
    const headings = renderIndex([taiki, kyla], creatorName)
      .split("\n")
      .filter((line) => line.startsWith("## "));

    expect(headings).toEqual(["## Kyla Scanlon", "## Taiki Maeda"]);
  });

  it("orders entries within a Creator newest first", () => {
    const titles = renderIndex([kylaOlder, kyla], creatorName)
      .split("\n")
      .filter((line) => line.startsWith("- "))
      .map((line) => line.slice(3, line.indexOf("]")));

    expect(titles).toEqual(["AI Agents", "Older Post"]);
  });

  it("links each entry relative to wiki/index.md, with date, Creator, and Blurb", () => {
    expect(renderIndex([kyla], creatorName)).toBe(
      [
        "# Index",
        "",
        "## Kyla Scanlon",
        "",
        "- [AI Agents](summaries/kyla-scanlon/2026-09-05-ai-agents.md) — 2026-09-05 · Kyla Scanlon — Agents edited a wiki into an answer key.",
        "",
      ].join("\n"),
    );
  });

  it("still produces a readable file when there are no Summaries", () => {
    expect(renderIndex([], creatorName)).toBe("# Index\n");
  });
});
