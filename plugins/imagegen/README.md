# ImageGen Plugin for Claude Code

AI-powered image generation using **Google Gemini** (Imagen) and **OpenAI GPT-Image**. Generate, edit, iterate, and create project assets directly from Claude Code.

## Features

- **Generate Images** - Create images from text prompts
- **Edit Images** - Modify existing images with AI
- **Iterate** - Multi-step refinement with session tracking
- **Compare Providers** - Side-by-side comparison of outputs
- **Asset Pipeline** - Generate app icons, favicons, social images
- **Moodboards** - Create design inspiration collections
- **Character Sheets** - Consistent character designs across poses

## Installation

```bash
# From the marketplace
/plugin marketplace add github:ThrownLemon/claude-code-plugins
/plugin install imagegen
```

## Prerequisites

### API Keys

Set your API keys as environment variables:

```bash
# Google Gemini
export GEMINI_API_KEY=your_google_api_key
# or
export GOOGLE_API_KEY=your_google_api_key

# OpenAI GPT-Image
export OPENAI_API_KEY=your_openai_api_key
```

### Python Packages

```bash
pip install google-genai openai Pillow
```

## Commands

| Command | Description |
|---------|-------------|
| `/imagegen:generate` | Generate images from text prompts |
| `/imagegen:edit` | Edit existing images with instructions |
| `/imagegen:iterate` | Iteratively refine images |
| `/imagegen:compare` | Compare Google vs OpenAI outputs |
| `/imagegen:assets` | Generate project assets |
| `/imagegen:moodboard` | Create design inspiration sets |
| `/imagegen:character` | Generate character sheets |
| `/imagegen:config` | Configure plugin settings |

## Quick Examples

### Generate an Image

```
/imagegen:generate --prompt "A serene mountain lake at sunset with reflections"
```

### Edit an Image

```
/imagegen:edit --image photo.png --prompt "Add dramatic storm clouds"
```

### Create App Icons

```
/imagegen:assets --type icons --prompt "Minimalist owl logo in blue and white"
```

### Generate a Moodboard

```
/imagegen:moodboard --theme "Cozy coffee shop" --style watercolor --variations 6
```

### Create Character Sheet

```
/imagegen:character --description "Young wizard with blue robes" --poses turnaround --style anime
```

### Compare Providers

```
/imagegen:compare --prompt "Futuristic cityscape at night"
```

## Providers

### Google Gemini (Imagen)

| Model | Description |
|-------|-------------|
| `gemini-2.5-flash-image` | Fast, efficient (default) |
| `gemini-3-pro-image-preview` | Professional quality, better consistency |

**Best for:**
- Character consistency
- Multi-turn iteration
- Style variety
- Cost efficiency

### OpenAI GPT-Image

| Model | Description |
|-------|-------------|
| `gpt-image-1-mini` | Fast, lower cost |
| `gpt-image-1` | Balanced (default) |
| `gpt-image-1.5` | Highest quality |

**Best for:**
- Text in images
- Transparent backgrounds
- Precise edits with masks

## Configuration

View and modify default settings:

```
/imagegen:config                                    # Show current config
/imagegen:config --action set --key default_provider --value openai
/imagegen:config --action set --key google.model --value gemini-3-pro-image-preview
```

Configuration file: `~/.config/claude-imagegen/config.json`

### Options

| Setting | Default | Description |
|---------|---------|-------------|
| `default_provider` | google | Default provider |
| `output_dir` | ./generated-images | Output directory |
| `google.model` | gemini-2.5-flash-image | Default Google model |
| `google.aspect_ratio` | 1:1 | Default aspect ratio |
| `openai.model` | gpt-image-1 | Default OpenAI model |
| `openai.size` | 1024x1024 | Default size |
| `openai.quality` | high | Default quality |

## Asset Types

### Icons (`/imagegen:assets --type icons`)
- Sizes: 16, 32, 48, 64, 128, 256, 512, 1024px
- Perfect for iOS, Android, macOS, Windows apps

### Favicons (`/imagegen:assets --type favicons`)
- PNG files + favicon.ico
- apple-touch-icon.png included

### Social (`/imagegen:assets --type social`)
- Open Graph (1200x630)
- Twitter Card (1200x628)
- LinkedIn Banner (1200x627)
- Instagram Post (1080x1080)
- Instagram Story (1080x1920)

### Thumbnails (`/imagegen:assets --type thumbnails`)
- YouTube (1280x720)
- Blog (800x450)
- Square (800x800)

## Iteration Sessions

Track refinements across multiple steps:

```bash
# Start a new session
/imagegen:iterate --image base.png --prompt "Make it more vibrant"
# Session ID: abc123

# Continue the session
/imagegen:iterate --session abc123 --prompt "Add more detail to the sky"

# List active sessions
/imagegen:iterate --list
```

Sessions are stored at `~/.config/claude-imagegen/sessions/`

## Character Consistency

For consistent character designs, the plugin:

1. Generates an initial reference image
2. Uses it as context for subsequent poses
3. Leverages Gemini's multi-turn capabilities

### Pose Presets

- `standard` - front, three-quarter, side, back
- `action` - standing, running, jumping, sitting
- `expressions` - neutral, happy, angry, sad
- `turnaround` - full rotation
- `headshots` - face angles

### Art Styles

- `anime`, `realistic`, `cartoon`, `pixel`
- `watercolor`, `comic`, `chibi`, `concept`
- `3d`, `sketch`

## Output Structure

```
generated-images/
├── img_20240115_143022_abc123.png    # Generated images
├── comparisons/                       # Provider comparisons
├── assets/
│   ├── icons/                         # App icons
│   ├── favicons/                      # Web favicons
│   └── social/                        # Social media images
├── moodboards/
│   └── theme_timestamp/               # Moodboard sets
└── characters/
    └── description_timestamp/         # Character sheets
```

## Tips

### Effective Prompts

- Be specific about style: "photorealistic", "watercolor painting", "minimalist vector"
- Include lighting: "golden hour", "dramatic shadows", "soft diffused light"
- Specify composition: "close-up", "wide establishing shot", "centered"
- Mention important details first

### Provider Selection

| Use Case | Recommended |
|----------|-------------|
| Quick generation | Google Flash |
| Text in images | OpenAI |
| Character consistency | Google Pro |
| Transparent backgrounds | OpenAI |
| Iteration/refinement | Google |
| Cost optimization | Google Flash or OpenAI Mini |

## Troubleshooting

### API Key Not Found
```
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

### Package Not Installed
```bash
pip install google-genai openai Pillow
```

### Rate Limits
- Switch to a different provider temporarily
- Wait and retry
- Use a smaller/faster model

## License

MIT License - See repository for details.

## Resources

- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs/imagen)
- [OpenAI Images API Docs](https://platform.openai.com/docs/guides/image-generation)
- [Claude Code Plugins Guide](https://github.com/anthropics/claude-code/tree/main/plugins)
