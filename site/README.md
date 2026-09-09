# Site

The reading site: a static Astro build of `wiki/summaries/**/*.md`. See
`docs/adr/0001-astro-static-site-no-runtime-state.md` for why it is Astro, static, and React-free.

```sh
npm install
npm run dev     # reads the working tree, so an uncommitted Summary previews
npm run build   # fails by name and field on a Summary missing frontmatter
npm test        # the mdast plugin that strips the authored header
npm run check   # typecheck
```

## How a Summary becomes a page

`src/content.config.ts` globs `../wiki/summaries` with a strict schema. A Summary
missing a required field fails the build — that error is how the summarize skill
finds out it forgot one, so don't soften the schema to make a build pass.

Summaries repeat their title and byline in the body so they read standalone in
Obsidian; `src/lib/strip-authored-header.ts` drops those two nodes so the Site can
render its header from validated frontmatter instead.

Raw is never globbed, routed, or linked. It stays out of the published site — the
one thing read from it is `duration`, which belongs to the Source rather than the
Summary and so was never added to the frontmatter contract.

## Deploying

Vercel builds from the repo root, not this directory, because the content lives
outside it. `vercel.json` at the root points the install, build, and output at
`site/`. A push to `main` deploys.
