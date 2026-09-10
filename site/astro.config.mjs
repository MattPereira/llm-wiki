// @ts-check
import { defineConfig } from "astro/config";
import { satteri } from "@astrojs/markdown-satteri";
import tailwindcss from "@tailwindcss/vite";
import { stripAuthoredHeader } from "./src/lib/strip-authored-header.ts";

export default defineConfig({
  markdown: {
    // Both themes render inline; global.css swaps to the dark one.
    shikiConfig: { themes: { light: "github-light", dark: "github-dark-dimmed" } },
    processor: satteri({ mdastPlugins: [stripAuthoredHeader] }),
  },
  vite: {
    plugins: [tailwindcss()],
    // Summaries live outside site/, so the dev server has to read up a level.
    server: { fs: { allow: [".."] } },
  },
});
