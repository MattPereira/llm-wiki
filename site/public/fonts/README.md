# Vendored fonts

Static latin subsets, committed rather than pulled at build time so a font
update can never silently reflow the site.

| File | Family | Weight | Source |
| --- | --- | --- | --- |
| `inter-latin-400-normal.woff2` | Inter | 400 | `@fontsource/inter@5` |
| `inter-latin-600-normal.woff2` | Inter | 600 | `@fontsource/inter@5` |
| `source-serif-4-latin-500-normal.woff2` | Source Serif 4 | 500 | `@fontsource/source-serif-4@5` |
| `source-serif-4-latin-600-normal.woff2` | Source Serif 4 | 600 | `@fontsource/source-serif-4@5` |

Both families are SIL Open Font License 1.1.

Declared in `src/styles/global.css`; the two faces above the fold on every page
are preloaded in `src/layouts/Base.astro`.
