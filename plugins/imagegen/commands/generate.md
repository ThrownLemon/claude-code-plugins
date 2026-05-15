---
description: Generate images from text prompts using Google Gemini or OpenAI GPT-Image
arguments:
  - name: prompt
    description: Text description of the image to generate
    required: true
  - name: provider
    description: "Provider to use: google or openai (default: from config)"
    required: false
  - name: model
    description: Specific model to use (e.g., gemini-2.5-flash-image, gpt-image-2)
    required: false
  - name: size
    description: "Size/aspect ratio (1:1, 16:9, landscape, portrait, square)"
    required: false
  - name: count
    description: Number of images to generate (1-4)
    required: false
  - name: output
    description: Output file path (default: auto-generated in output directory)
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Generate Image

Generate AI images from text prompts using either Google Gemini (Gemini) or OpenAI GPT-Image.

## Supported Providers

### Google Gemini (Gemini)
- **Models**: `gemini-2.5-flash-image` (fast), `gemini-3-pro-image-preview` (professional)
- **Features**: Multi-turn iteration, character consistency, up to 4K output
- **Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9

### OpenAI GPT-Image
- **Models**: `gpt-image-2` (default, state-of-the-art), `gpt-image-1.5`, `gpt-image-1` (only one with transparency support), `gpt-image-1-mini`
- **Features**: Excellent text rendering. gpt-image-2 has built-in reasoning ("thinking mode"). Transparent backgrounds available on gpt-image-1 only.
- **Sizes**: 1024x1024, 1536x1024 (landscape), 1024x1536 (portrait), 2048x2048

## Examples

```
/imagegen:generate --prompt "A serene mountain lake at sunset"
/imagegen:generate --prompt "Logo for a tech startup" --provider openai --size square
/imagegen:generate --prompt "Cyberpunk cityscape" --provider google --model gemini-3-pro-image-preview --size 16:9
/imagegen:generate --prompt "Cute robot mascot" --count 4
```

## Execution

Run the generate script with the provided arguments:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate.py \
  --prompt "$ARGUMENTS.prompt" \
  ${ARGUMENTS.provider:+--provider "$ARGUMENTS.provider"} \
  ${ARGUMENTS.model:+--model "$ARGUMENTS.model"} \
  ${ARGUMENTS.size:+--size "$ARGUMENTS.size"} \
  ${ARGUMENTS.count:+--count "$ARGUMENTS.count"} \
  ${ARGUMENTS.output:+--output "$ARGUMENTS.output"}
```

After generation:
1. Display the generated image path(s)
2. Offer to open/view the image
3. Suggest iteration if user wants to refine

## Environment Variables Required

- **Google**: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- **OpenAI**: `OPENAI_API_KEY`
