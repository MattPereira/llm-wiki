import { describe, expect, it } from "vitest";
import { activeNav } from "./nav.js";

describe("activeNav", () => {
  it("marks Summaries on the home feed", () => {
    expect(activeNav("/")).toBe("/");
  });

  it("marks the section for each index", () => {
    expect(activeNav("/creators/")).toBe("/creators/");
    expect(activeNav("/topics/")).toBe("/topics/");
    expect(activeNav("/search/")).toBe("/search/");
  });

  it("tolerates a missing trailing slash, which is what the dev server serves", () => {
    expect(activeNav("/topics")).toBe("/topics/");
  });

  it("marks Topics on a single Topic page", () => {
    expect(activeNav("/topics/ai/")).toBe("/topics/");
  });

  it("marks Creators on a Creator page", () => {
    expect(activeNav("/kyla-scanlon/")).toBe("/creators/");
  });

  it("marks nothing on a Summary, which is a leaf rather than a section", () => {
    expect(activeNav("/kyla-scanlon/2026-09-05-ai-agents/")).toBeUndefined();
  });
});
