# Astro static site; markdown stays the sole source of truth

The wiki needs a readable web front-end deployable to Vercel. We build it as a
static Astro site in `site/` within this repo, generated at build time from
`wiki/summaries/**/*.md`. It has no server, no database, and no runtime state:
every byte it renders comes from a markdown file in git, and `git push` is the
only way to change what it shows.

## Considered options

- **Next.js + Neon + GitHub OAuth.** Reached seriously while cross-device read
  tracking was in scope. Dropping read tracking removed the only requirement for
  a server, and with it the DB, the auth, and the identity model.
- **Starlight** (Astro's docs theme). Gives sidebar, search, and typography free,
  but is shaped like a manual. What we want is a dated reverse-chron archive
  browsable by creator and topic, which means fighting the sidebar.
- **React + shadcn/ui.** Officially supported in Astro but requires the React
  integration. Deferred: the only interaction worth the runtime cost was a `⌘K`
  search palette, and Pagefind's own vanilla UI covers search without it.
- **Read tracking.** Wanted, then dropped twice. Cross-device needs a backend;
  per-device localStorage doesn't, and can be added later without architectural
  change. Neither is in v1.

## Consequences

- The Site never writes. Personal state (read/unread, notes, highlights) has no
  home in this design — if such state must become durable, it becomes a markdown
  file an agent writes, not a database row.
- Summary frontmatter is validated by a strict content-collection schema. A
  Summary missing `blurb` or `topics` fails the build. This is deliberate: the
  schema is the contract the summarize skill must honour, and a build error is
  the fastest way to tell it so.
- `wiki/index.md` becomes a build artifact generated from summary frontmatter
  rather than a hand-authored file, so the Blurb lives in exactly one place.
- Raw is never published, so it is never searchable from the web. Pagefind
  indexes built HTML, which is Summaries only.
- Permalinks mirror the file tree (`/<creator>/<date>-<slug>`). A creator rename
  breaks old URLs; acceptable for a single reader.

## Deployment

Vercel builds from the repo root with `vercel.json`, not with its Root Directory
pointed at `site/`. The Root Directory setting prunes everything above it, which
would take `wiki/summaries/` — the entire content source — out of the build.
