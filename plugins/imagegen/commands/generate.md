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
    description: Specific model to use (e.g., gemini-2.5-flash-image, gpt-image-1.5)
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

# Generate Image

Generate AI images from text prompts using either Google Gemini (Gemini) or OpenAI GPT-Image.

## Supported Providers

### Google Gemini (Gemini)
- **Models**: `gemini-2.5-flash-image` (fast), `gemini-3-pro-image-preview` (professional)
- **Features**: Multi-turn iteration, character consistency, up to 4K output
- **Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9

### OpenAI GPT-Image
- **Models**: `gpt-image-1.5` (best), `gpt-image-1`, `gpt-image-1-mini`
- **Features**: Transparent backgrounds, excellent text rendering
- **Sizes**: 1024x1024, 1536x1024 (landscape), 1024x1536 (portrait)

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
