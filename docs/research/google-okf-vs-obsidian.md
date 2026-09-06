# Google OKF vs. Obsidian

## Conclusion

Not mutually exclusive. Best fit: **OKF = knowledge format; Obsidian = human UI over it; Git + agents = workflow.** Google explicitly lists Obsidian as an OKF consumer. [OKF README](https://github.com/GoogleCloudPlatform/open-knowledge-format#open-knowledge-format-okf)

## What each contributes

| Layer | OKF | Obsidian |
|---|---|---|
| Purpose | Portable contract for agent/human knowledge | Local authoring, browsing, search, graph, views |
| Storage | Markdown tree + YAML frontmatter | Vault: local folder of Markdown files |
| Structure | One concept/file; path is ID; normal Markdown links form graph | Folders, links, backlinks, graph |
| Metadata | Requires `type`; recommends title, description, resource, tags; v0.2 adds provenance/trust/freshness | Reads YAML properties; can search/query them |
| Runtime | Intentionally does not prescribe storage, serving, query, model, or agent | Application/UI; not an interoperability or provenance standard |

Sources: [OKF v0.2 spec](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md), [Obsidian data storage](https://obsidian.md/help/data-storage), [Obsidian properties](https://obsidian.md/help/properties), [Obsidian graph](https://obsidian.md/help/plugins/graph).

## OKF pattern

- Bundle = directory tree; Git recommended; may be a subdirectory of a larger repo.
- Concept = one Markdown document. YAML `type` is the only always-required field. Body stays free-form, structured Markdown.
- Normal Markdown links add graph edges beyond folder hierarchy.
- Optional `index.md` supports progressive disclosure; optional `log.md` records chronology.
- v0.2 makes `sources`, `generated`, `verified`, `status`, and `stale_after` machine-readable. These distinguish provenance, human review, and freshness.
- It does **not** define ingestion, summarization prompts, embeddings/RAG, serving, or UI.

These are direct requirements/non-goals from the [canonical v0.2 spec](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Google describes OKF as formalizing the LLM-wiki pattern, including Obsidian vaults wired to coding agents. [Google Cloud announcement](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)

## Combined design for this repo

Open the repo root as one Obsidian vault. Keep the conforming bundle isolated:

```text
wiki/
├── .obsidian/             # optional local UI configuration
├── content/               # raw ingested articles/transcripts
├── scripts/               # ingestion/maintenance
├── okf/                   # portable distilled knowledge bundle
│   ├── index.md
│   ├── log.md
│   ├── sources/           # one article/video summary per concept
│   └── topics/            # cross-source synthesis
├── README.md
└── CONTENT.md
```

Why isolate `okf/`: strict conformance treats every non-reserved `.md` under the bundle as a concept requiring frontmatter and `type`. The current repo-root `README.md`, `CONTENT.md`, and agent docs are not concepts. The spec explicitly permits a bundle as a subdirectory. [Bundle and conformance rules](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#3-bundle-structure)

Suggested flow:

1. Ingest raw material into `content/`.
2. Agent writes/updates distilled concepts in `okf/`, recording source URLs, generation time, status, and review.
3. Agent regenerates nearby `index.md` files.
4. Human reviews in Obsidian; Git preserves diffs/history.
5. Agents begin at `okf/index.md`, then progressively open relevant concepts.

## Compatibility rules

- Use normal Markdown links, not `[[wikilinks]]`; Obsidian supports both and recommends Markdown links when interoperability matters. Avoid Obsidian-only block references. [Obsidian links](https://obsidian.md/help/links)
- Keep filenames simple/kebab-case; prefer relative `.md` links.
- Keep OKF v0.2 nested metadata intact. Obsidian's Properties UI does not support nested properties; edit/view those in source mode. Simple fields such as `type`, `title`, and `tags` remain convenient in the UI. [Obsidian properties limitations](https://obsidian.md/help/properties#Not%20supported)
- Obsidian Bases can query note frontmatter and make table-like views; `.base` files do not affect OKF's Markdown conformance. [Bases syntax](https://obsidian.md/help/bases/syntax)
- Keep `.obsidian/` at repo root, not another nested vault; Obsidian warns nested vault links may update incorrectly. [Vault storage](https://obsidian.md/help/data-storage)

## Version/link trap

The June 2026 Google blog documents v0.1 (`timestamp`, body citation list). Current canonical spec is v0.2 (`generated.at`, frontmatter `sources`) and supersedes v0.1. Also, the README's `knowledge-catalog/okf` link now says that copy is frozen and redirects readers to `GoogleCloudPlatform/open-knowledge-format`. Build against the [canonical repository](https://github.com/GoogleCloudPlatform/open-knowledge-format) and [v0.2 migration notes](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md#13-changes-from-v01).
