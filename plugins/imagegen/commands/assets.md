---
description: Generate project assets like app icons, favicons, social images
arguments:
  - name: type
    description: "Asset type: icons, favicons, social, or thumbnails"
    required: true
  - name: prompt
    description: Description/theme for the assets
    required: true
  - name: variants
    description: Specific variants to generate (for social/thumbnails)
    required: false
  - name: output-dir
    description: Output directory
    required: false
---

# Asset Pipeline

Generate complete asset sets for your project including app icons, favicons, social media images, and thumbnails.

## Asset Types

### Icons (`icons`)
App icons in multiple sizes for iOS, Android, macOS, Windows:
- Sizes: 16, 32, 48, 64, 128, 256, 512, 1024px

### Favicons (`favicons`)
Web favicons and touch icons:
- PNG files: 16, 32, 48, 180, 192, 512px
- favicon.ico (multi-resolution)
- apple-touch-icon.png

### Social (`social`)
Social media images:
- `og` - Open Graph (1200x630)
- `twitter` - Twitter Card (1200x628)
- `linkedin` - LinkedIn Banner (1200x627)
- `instagram` - Instagram Post (1080x1080)
- `instagram_story` - Instagram Story (1080x1920)

### Thumbnails (`thumbnails`)
Content thumbnails:
- `youtube` - YouTube thumbnail (1280x720)
- `vimeo` - Vimeo thumbnail (1280x720)
- `blog` - Blog post image (800x450)
- `square` - Square thumbnail (800x800)

## Examples

```
/imagegen:assets --type icons --prompt "Minimalist owl logo in blue"
/imagegen:assets --type favicons --prompt "Letter T in a circle"
/imagegen:assets --type social --prompt "Tech blog header with abstract shapes"
/imagegen:assets --type social --prompt "Product launch" --variants og twitter
/imagegen:assets --type thumbnails --prompt "Tutorial video cover"
```

## Execution

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assets.py \
  --type "$ARGUMENTS.type" \
  --prompt "$ARGUMENTS.prompt" \
  ${ARGUMENTS.variants:+--variants $ARGUMENTS.variants} \
  ${ARGUMENTS.output-dir:+--output-dir "$ARGUMENTS.output-dir"}
```

To list variants for a type:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assets.py --type social --list-variants
```

## Output Structure

```
assets/
├── icons/
│   ├── icon_base.png
│   ├── icon_16.png
│   ├── icon_32.png
│   └── ...
├── favicons/
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   └── ...
└── social/
    ├── og-image.png
    ├── twitter-card.png
    └── ...
```

## Requirements

- PIL/Pillow for resizing: `pip install Pillow`
- API key for chosen provider
