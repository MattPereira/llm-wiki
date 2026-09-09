import { describe, expect, it } from "vitest";
import {
  assertRoutableCreators,
  creatorName,
  creatorSlugs,
  parseCreators,
} from "./creators.js";

describe("parseCreators", () => {
  it("maps each table key to its name", () => {
    const creators = parseCreators(`
[kyla-scanlon]
name = "Kyla Scanlon"
youtube = ["kyla-scanlon"]
`);

    expect(creators.get("kyla-scanlon")).toBe("Kyla Scanlon");
  });

  it("keeps quoted keys, which is how a numeric-looking slug survives", () => {
    const creators = parseCreators(`
["1000x"]
name = "1000x"
`);

    expect([...creators.keys()]).toEqual(["1000x"]);
  });

  it("rejects an entry without a name rather than let a slug reach a page", () => {
    expect(() => parseCreators(`[nameless]\nyoutube = ["nameless"]\n`)).toThrow(
      /nameless/,
    );
  });
});

describe("creatorName", () => {
  it("reads the real creators.toml", () => {
    expect(creatorName("taiki-maeda")).toBe("Taiki Maeda");
  });

  it("fails loudly for a slug creators.toml does not define", () => {
    expect(() => creatorName("who-dis")).toThrow(/who-dis/);
  });
});

describe("creatorSlugs", () => {
  it("lists every creator the file defines", () => {
    expect(creatorSlugs()).toContain("arthur-hayes");
  });
});

describe("assertRoutableCreators", () => {
  it("passes the real creators.toml", () => {
    expect(() => assertRoutableCreators()).not.toThrow();
  });

  it("refuses a slug the site's own pages would shadow", () => {
    expect(() => assertRoutableCreators(["topics"])).toThrow(/topics/);
  });

  it("allows a slug that merely contains a reserved word", () => {
    expect(() => assertRoutableCreators(["topics-daily"])).not.toThrow();
  });
});
