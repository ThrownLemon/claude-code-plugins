---
description: Generate consistent character sheets with multiple poses and views
arguments:
  - name: description
    description: Character description
    required: true
  - name: reference
    description: Reference image for character consistency
    required: false
  - name: poses
    description: "Comma-separated poses or preset (standard, action, expressions, turnaround, headshots)"
    required: false
  - name: style
    description: "Art style (anime, realistic, cartoon, pixel, etc.)"
    required: false
---

# Character Sheet Generator

Create consistent character designs across multiple poses and views. Leverages Gemini's character consistency features for best results.

## Pose Presets

- `standard` - front, three-quarter, side, back views
- `action` - standing, running, jumping, sitting
- `expressions` - neutral, happy, angry, sad
- `turnaround` - full rotation views
- `headshots` - face from various angles

## Art Styles

- `anime` - Cel shaded, vibrant
- `realistic` - Photorealistic, lifelike
- `cartoon` - Bold outlines, exaggerated
- `pixel` - Retro gaming aesthetic
- `watercolor` - Soft, artistic
- `comic` - Dynamic, bold colors
- `chibi` - Cute, big head style
- `concept` - Professional concept art
- `3d` - 3D rendered, stylized
- `sketch` - Hand-drawn look

## Examples

```
/imagegen:character --description "A young wizard with blue robes and a wooden staff"
/imagegen:character --description "Robot companion with friendly face" --poses action --style cartoon
/imagegen:character --description "Elven archer" --poses turnaround --style concept
/imagegen:character --description "Pirate captain" --reference existing_design.png --poses expressions
```

## Execution

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/character.py \
  --description "$ARGUMENTS.description" \
  ${ARGUMENTS.reference:+--reference "$ARGUMENTS.reference"} \
  ${ARGUMENTS.poses:+--poses "$ARGUMENTS.poses"} \
  ${ARGUMENTS.style:+--style "$ARGUMENTS.style"}
```

To list presets and styles:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/character.py --list-presets
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/character.py --list-styles
```

## Output

Creates a character folder with:
- Multiple pose images (character_01_front_view.png, etc.)
- `character_meta.json` with description and settings

## Consistency Tips

- **Use Google provider** - Best for maintaining character consistency
- **Provide reference** - If you have a starting design, use it
- **Be specific** - Include distinctive features in description
- **Gemini 3 Pro** - Automatically used for better consistency

## Workflow

1. Generate initial character
2. Use result as reference for more poses
3. Iterate to refine the design
4. Build complete character sheet
