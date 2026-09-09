import { describe, expect, it } from "vitest";
import { fileURLToPath } from "node:url";
import { formatDuration, readDurationSeconds } from "./duration.js";

describe("formatDuration", () => {
  it("renders minutes and seconds", () => {
    expect(formatDuration(177)).toBe("2:57");
  });

  it("pads seconds", () => {
    expect(formatDuration(65)).toBe("1:05");
  });

  it("renders hours when there are any", () => {
    expect(formatDuration(3967)).toBe("1:06:07");
  });

  it("pads minutes once hours are shown", () => {
    expect(formatDuration(3605)).toBe("1:00:05");
  });
});

describe("readDurationSeconds", () => {
  const raws = fileURLToPath(new URL("../../../wiki/raw", import.meta.url));

  it("reads the duration off the Raw a Summary points at", () => {
    expect(
      readDurationSeconds(
        `${raws}/kyla-scanlon/2026-09-05-ai-agents.md`,
      ),
    ).toBe(177);
  });

  it("returns undefined for a Raw with no duration, such as a Substack post", () => {
    expect(
      readDurationSeconds(`${raws}/arthur-hayes/2026-09-02-atencion.md`),
    ).toBeUndefined();
  });

  it("returns undefined when the Raw is missing rather than failing the build", () => {
    expect(readDurationSeconds(`${raws}/nobody/nothing.md`)).toBeUndefined();
  });
});
