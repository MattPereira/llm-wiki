import { describe, expect, it } from "vitest";
import { markdownToHtml } from "satteri";
import { stripAuthoredHeader } from "./strip-authored-header.js";

const run = (md: string) =>
  markdownToHtml(md, { mdastPlugins: [stripAuthoredHeader] }).html.trim();

describe("stripAuthoredHeader", () => {
  it("drops the leading h1 and the byline that follows it", () => {
    const out = run(
      [
        "# AI Agents",
        "",
        "**Kyla Scanlon** · 2026-09-05 · 2:57 · [watch](https://youtu.be/x)",
        "",
        "## Thesis",
        "",
        "Body.",
      ].join("\n"),
    );
    expect(out).toBe("<h2>Thesis</h2>\n<p>Body.</p>");
  });

  it("drops a leading h1 that has no byline after it", () => {
    expect(run("# Title\n\n## Thesis")).toBe("<h2>Thesis</h2>");
  });

  it("leaves a paragraph that only looks like prose alone", () => {
    expect(run("# Title\n\nAn opening paragraph.")).toBe(
      "<p>An opening paragraph.</p>",
    );
  });

  it("leaves a document that does not start with an h1 alone", () => {
    expect(run("## Thesis\n\nBody.")).toBe("<h2>Thesis</h2>\n<p>Body.</p>");
  });

  it("never strips a byline-shaped paragraph deeper in the document", () => {
    expect(run("## Thesis\n\n**A** · 2026-01-01")).toBe(
      "<h2>Thesis</h2>\n<p><strong>A</strong> · 2026-01-01</p>",
    );
  });
});
