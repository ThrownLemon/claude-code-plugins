# check-models

A zero-dependency maintainer tool that keeps the marketplace's AI model ids
current. It **discovers every model id used across the repo**, queries each
provider's live `/models` endpoint, and reports what's current, what to verify,
and which newer models you aren't using yet.

This is a dev-tool, not a plugin — model ids go stale fast and this gives a
quick, repeatable currency check.

## Usage

```bash
# Check every provider whose API key is set in the environment
node tools/check-models/check-models.mjs

# One provider only
node tools/check-models/check-models.mjs --provider zai

# Machine-readable
node tools/check-models/check-models.mjs --json

# Exit non-zero if any configured id is missing from a live list (for CI)
node tools/check-models/check-models.mjs --strict
```

### API keys (only providers with a key are checked)

| Provider | Env var(s) |
|----------|------------|
| Z.AI (GLM) | `ZAI_API_KEY` / `ZHIPU_API_KEY` / `GLM_API_KEY` |
| OpenAI (gpt-image, sora) | `OPENAI_API_KEY` |
| Google (gemini, veo, imagen) | `GEMINI_API_KEY` / `GOOGLE_API_KEY` |

## How to read the output

| Symbol | Meaning |
|--------|---------|
| `✓` | Configured id is in the provider's live `/models` list — current. |
| `↻` | Rolling alias (`*-latest`) — always current by definition. |
| `↳` | Friendly shortform of a real live id (e.g. `veo-3.1` → `veo-3.1-generate-preview`). Not a problem. |
| `⚠` | Configured id is **not** in the live list — verify. Some valid models aren't always listed (e.g. a brand-new flagship), so this means "check", not "broken". |
| `🆕` | Live models the repo doesn't reference yet — candidates, including newer releases. |

## What it scans

Every text file in the repo (code, configs, docs) except `.git`,
`node_modules`, this tool's own directory, and `AUDIT-*.md`. Model ids are
matched per provider with version-aware patterns, so prose like `gemini-cli` or
`glm-5.x` is ignored.

## Scheduled run

`.github/workflows/check-models.yml` runs this weekly (and on demand) and writes
the report to the workflow summary. Add `ZAI_API_KEY`, `OPENAI_API_KEY`, and
`GEMINI_API_KEY` as repository secrets to enable the providers you want checked.

## Tests

```bash
node --test tools/check-models/lib.test.mjs
```
