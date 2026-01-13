---
description: Generate moodboard with multiple related images for design inspiration
arguments:
  - name: theme
    description: Main theme or concept for the moodboard
    required: true
  - name: style
    description: "Art style (realistic, watercolor, minimal, vintage, neon, etc.)"
    required: false
  - name: variations
    description: Number of variations to generate (default: 4)
    required: false
  - name: aspects
    description: Use different aspect ratios for variety
    required: false
---

# Moodboard Generator

Create multiple related images around a central theme for design inspiration, creative exploration, or visual brainstorming.

## Available Styles

- `realistic` - Photorealistic, detailed
- `watercolor` - Soft watercolor painting
- `minimal` - Minimalist, clean lines
- `vintage` - Retro, nostalgic
- `neon` - Vibrant neon colors
- `pastel` - Soft pastel tones
- `dark` - Moody, dramatic
- `bright` - Cheerful, high key
- `abstract` - Conceptual, artistic
- `sketch` - Pencil sketch style
- `3d` - 3D rendered
- `flat` - Flat design, graphic

## Examples

```
/imagegen:moodboard --theme "Cozy coffee shop interior"
/imagegen:moodboard --theme "Cyberpunk city" --style neon --variations 6
/imagegen:moodboard --theme "Sustainable fashion brand" --style minimal --aspects
/imagegen:moodboard --theme "Fantasy forest" --style watercolor
```

## Execution

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/moodboard.py \
  --theme "$ARGUMENTS.theme" \
  ${ARGUMENTS.style:+--style "$ARGUMENTS.style"} \
  ${ARGUMENTS.variations:+--variations "$ARGUMENTS.variations"} \
  ${ARGUMENTS.aspects:+--aspects}
```

To list available styles:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/moodboard.py --list-styles
```

## Output

Creates a timestamped folder with:
- Multiple image variations
- `moodboard_meta.json` with all prompts used

## Variation Angles

Each image in the moodboard uses different angles/compositions:
- Wide establishing shots
- Close-up details
- Bird's eye views
- Dynamic angles
- Various lighting conditions
- Different moods (vibrant, serene, dramatic)

## Tips

- Keep themes focused but not too specific
- Use style modifiers for cohesive results
- Generate 4-6 images for good variety
- Use `--aspects` for diverse compositions
