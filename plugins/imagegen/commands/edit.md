---
description: Edit existing images using AI-powered text instructions
arguments:
  - name: image
    description: Path to the image to edit
    required: true
  - name: prompt
    description: Edit instructions (what changes to make)
    required: true
  - name: provider
    description: "Provider to use: google or openai"
    required: false
  - name: mask
    description: Path to mask image for inpainting (OpenAI only)
    required: false
  - name: output
    description: Output file path
    required: false
---

# Edit Image

Edit existing images using AI text instructions. Supports modifications like style changes, adding/removing elements, color adjustments, and more.

## How It Works

### Google (Gemini)
- Send image + text prompt together
- Model understands context and applies edits
- Supports semantic understanding for complex edits
- Best for: style transfer, modifications, enhancements

### OpenAI (GPT-Image)
- Uses the images/edit endpoint
- Optional mask for targeted inpainting
- Best for: precise edits with masks, object removal

## Examples

```
/imagegen:edit --image photo.png --prompt "Add a rainbow in the sky"
/imagegen:edit --image portrait.jpg --prompt "Convert to watercolor painting style"
/imagegen:edit --image logo.png --prompt "Change the color scheme to blue and gold"
/imagegen:edit --image scene.png --prompt "Remove the person on the left" --provider openai --mask mask.png
```

## Execution

Run the edit script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/edit.py \
  --image "$ARGUMENTS.image" \
  --prompt "$ARGUMENTS.prompt" \
  ${ARGUMENTS.provider:+--provider "$ARGUMENTS.provider"} \
  ${ARGUMENTS.mask:+--mask "$ARGUMENTS.mask"} \
  ${ARGUMENTS.output:+--output "$ARGUMENTS.output"}
```

After editing:
1. Display the edited image path
2. Show before/after comparison
3. Offer to iterate further

## Tips

- Be specific about what to change
- For precise edits, use OpenAI with a mask
- For style changes, Google often produces better results
- Complex edits may need multiple iterations
