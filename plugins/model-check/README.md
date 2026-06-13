# model-check

A zero-dependency plugin that keeps AI model ids from going stale. It
**discovers every model id used in a project**, queries each provider's live
`/models` endpoint (z.ai, OpenAI, Google), and reports what's current, what to
verify, and which newer models you aren't using yet.

Useful both as a maintainer dev-tool for this marketplace and against any
project that pins AI model ids.

## Usage

From Claude Code:

```
/model-check:check-models            # all providers with a key set
/model-check:check-models zai        # limit to one provider (zai|openai|gemini)
```

Or run the script directly:

```bash
node plugins/model-check/scripts/check-models.mjs            # all providers
node plugins/model-check/scripts/check-models.mjs --provider zai
node plugins/model-check/scripts/check-models.mjs --json     # machine-readable
node plugins/model-check/scripts/check-models.mjs --strict   # exit 1 if any id is missing (CI)
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
| `🆕` | Live models the project doesn't reference yet — candidates, including newer releases. |

## What it scans

Every text file under the project root (code, configs, docs) except `.git`,
`node_modules`, this plugin's own directory, and `AUDIT-*.md`. Model ids are
matched per provider with version-aware patterns, so prose like `gemini-cli` or
`glm-5.x` is ignored.

## Scheduled run

`.github/workflows/check-models.yml` runs the checker weekly (and on demand) and
writes the report to the workflow summary. Add `ZAI_API_KEY`, `OPENAI_API_KEY`,
and `GEMINI_API_KEY` as repository secrets to enable the providers you want
checked.

## Tests

```bash
node --test plugins/model-check/scripts/lib.test.mjs
```
