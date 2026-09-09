# Site

The reading site: a static Astro build of `wiki/summaries/**/*.md`. See
`docs/adr/0001-astro-static-site-no-runtime-state.md` for why it is Astro, static, and React-free.

```sh
npm install
npm run dev     # reads the working tree, so an uncommitted Summary previews
npm run build   # fails by name and field on a Summary missing frontmatter
npm test        # the pure lib/ seams: vocabulary parsing, grouping, formatting
npm run check   # typecheck
npm run generate-index  # rewrites wiki/index.md from Summary frontmatter
```

## How a Summary becomes a page

`src/content.config.ts` globs `../wiki/summaries` with a strict schema. A Summary
missing a required field fails the build — that error is how the summarize skill
finds out it forgot one, so don't soften the schema to make a build pass.

Summaries repeat their title and byline in the body so they read standalone in
Obsidian; `src/lib/strip-authored-header.ts` drops those two nodes so the Site can
render its header from validated frontmatter instead.

`wiki/index.md` is the agent-facing counterpart to those pages, and is generated
rather than written: `scripts/generate-index.ts` parses the same frontmatter
against the same schema and `src/lib/index-markdown.ts` renders it. The generator
lives here rather than beside the Python ingest scripts so there is one definition
of a valid Summary, not one per language.

Raw is never globbed, routed, or linked. It stays out of the published site — the
one thing read from it is `duration`, which belongs to the Source rather than the
Summary and so was never added to the frontmatter contract.

## Browsing across the wiki

`/` is every Summary newest-first. `/<creator>/` is one Creator's, `/creators` is
everyone the wiki holds a Summary for. `/topics/<topic>` gathers a Topic across
Creators and `/topics` is the whole vocabulary — including Topics nothing carries
yet, because a linked Topic that 404s is worse than one that says it is empty.

`/creators` is deliberately *not* the mirror of `/topics`: it lists only Creators
the wiki holds a Summary for, because `creators.toml` also carries Creators that
are merely configured for ingest. `/topics` lists its whole vocabulary because the
vocabulary is the point — a reader needs to see what the wiki does not cover.

`creators.toml` and `topics.toml` are read as TOML (`src/lib/vocabulary.ts`), not
converted to JSON: a third of their lines are comments carrying rules that live
nowhere else. Both are closed sets, and a slug outside either one fails the build
by name rather than rendering a slug or spawning an orphan page — an off-vocabulary
Topic in the content schema, an undefined Creator when `creatorName` is asked for
one. `assertRoutableCreators` additionally rejects a Creator slug that would be
shadowed by one of the site's own top-level pages.

Those files sit above this directory, so they are found by walking up from the cwd
rather than from `import.meta.url` — Astro bundles `src/lib/` into
`dist/.prerender/chunks/`, where a module-relative path points at nothing.

## Search

Pagefind runs as a `postbuild` step over `dist/`, so there is no server and no
hand-maintained index. Only Summary pages carry `data-pagefind-body`, which is
what confines the index to them — and since Raw is never built, a phrase dropped
from a Summary is not findable.

`/search` is the only page that loads JavaScript, and it loads Pagefind's own
inline. Under `npm run dev` there is no index yet, so the page says so; use
`npm run build && npm run preview` to try search.

## Deploying

Vercel builds from the repo root, not this directory, because the content lives
outside it. `vercel.json` at the root points the install, build, and output at
`site/`. A push to `main` deploys.
