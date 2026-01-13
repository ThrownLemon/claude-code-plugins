---
description: Configure imagegen plugin defaults and settings
arguments:
  - name: action
    description: "Action: show, set, get, path"
    required: false
  - name: key
    description: Configuration key (e.g., default_provider, google.model)
    required: false
  - name: value
    description: Value to set
    required: false
---

# Plugin Configuration

Configure default settings for the imagegen plugin including default provider, models, output directory, and more.

## Configuration Options

| Key | Description | Default |
|-----|-------------|---------|
| `default_provider` | Default provider (google/openai) | google |
| `output_dir` | Default output directory | ./generated-images |
| `google.model` | Default Google model | gemini-2.5-flash-image |
| `google.aspect_ratio` | Default aspect ratio | 1:1 |
| `openai.model` | Default OpenAI model | gpt-image-1 |
| `openai.size` | Default size | 1024x1024 |
| `openai.quality` | Default quality | high |
| `naming.prefix` | Filename prefix | img |
| `naming.include_timestamp` | Include timestamp in names | true |

## Examples

```
# Show current configuration
/imagegen:config

# Set default provider
/imagegen:config --action set --key default_provider --value openai

# Set default Google model
/imagegen:config --action set --key google.model --value gemini-3-pro-image-preview

# Get specific setting
/imagegen:config --action get --key output_dir

# Show config file path
/imagegen:config --action path
```

## Execution

Show config (default):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py
```

Set value:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py set "$ARGUMENTS.key" "$ARGUMENTS.value"
```

Get value:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py get "$ARGUMENTS.key"
```

Show path:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/config.py path
```

## Config File Location

Configuration is stored at:
`~/.config/claude-imagegen/config.json`

## Environment Variables

API keys are read from environment variables (not stored in config):
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` - Google Gemini
- `OPENAI_API_KEY` - OpenAI

Set these in your shell profile or `.env` file.

## Model Options

### Google Models
- `gemini-2.5-flash-image` - Fast, efficient
- `gemini-3-pro-image-preview` - Professional, better consistency

### OpenAI Models
- `gpt-image-1-mini` - Fast, lower cost
- `gpt-image-1` - Balanced
- `gpt-image-1.5` - Best quality
