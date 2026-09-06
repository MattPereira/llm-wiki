## Agent skills

### Issue tracker

Issues live as GitHub issues on `MattPereira/llm-wiki`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Ingestion

- **YouTube** — `scripts/ingest_youtube.py`, then the `ingest-youtube` skill supplies structure the transcript lacks.
- **Substack** — `uv run scripts/ingest_substack.py <post-url>`. No skill: the author already wrote the headings, so nothing after the fetch needs judgment. Exits `2` on paywalled posts and writes nothing, because the API serves a truncated preview with no marker in it.
