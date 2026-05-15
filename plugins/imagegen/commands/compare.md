---
description: Compare image generation between Google and OpenAI providers
arguments:
  - name: prompt
    description: Text prompt to generate with both providers
    required: true
  - name: google-model
    description: Google model to use (default: gemini-2.5-flash-image)
    required: false
  - name: openai-model
    description: OpenAI model to use (default: gpt-image-2)
    required: false
  - name: size
    description: Target size/aspect ratio
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Compare Providers

Generate the same prompt with both Google Gemini and OpenAI GPT-Image for side-by-side comparison. Useful for evaluating which provider produces better results for your specific use case.

## What Gets Generated

- One image from Google Gemini
- One image from OpenAI GPT-Image
- Metadata file with comparison details
- Estimated costs for each provider

## Examples

```
/imagegen:compare --prompt "A futuristic spaceship in orbit"
/imagegen:compare --prompt "Portrait of a wise old wizard" --google-model gemini-3-pro-image-preview
/imagegen:compare --prompt "Product photo of headphones" --size 16:9
```

## Execution

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compare.py \
  --prompt "$ARGUMENTS.prompt" \
  ${ARGUMENTS.google-model:+--google-model "$ARGUMENTS.google-model"} \
  ${ARGUMENTS.openai-model:+--openai-model "$ARGUMENTS.openai-model"} \
  ${ARGUMENTS.size:+--size "$ARGUMENTS.size"}
```

## Output

Creates a `comparisons/` folder with:
- `compare_TIMESTAMP_google.png` - Google's result
- `compare_TIMESTAMP_openai.png` - OpenAI's result
- `compare_TIMESTAMP_meta.json` - Metadata and costs

## Comparison Factors

Consider these when comparing:
- **Quality**: Detail, sharpness, artifacts
- **Prompt adherence**: How well it matches the description
- **Style**: Artistic interpretation differences
- **Text rendering**: If prompt includes text
- **Cost**: Price per image
- **Speed**: Generation time

## Requirements

Both API keys must be set:
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
