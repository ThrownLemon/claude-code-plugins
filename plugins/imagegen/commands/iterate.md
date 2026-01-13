---
description: Iteratively refine images through multiple generation steps
arguments:
  - name: image
    description: Starting image path (for new session)
    required: false
  - name: session
    description: Session ID to continue existing iteration
    required: false
  - name: prompt
    description: Refinement instructions
    required: true
  - name: list
    description: List active iteration sessions
    required: false
---

# Iterate on Images

Refine images through multiple generation steps. Creates a session that maintains context across iterations, especially powerful with Google Gemini's multi-turn capabilities.

## How Sessions Work

1. **Start a new session** with an initial image
2. **Iterate** with text prompts to refine
3. **Continue** the session with more refinements
4. Each step uses the previous result as reference

## Examples

```
# Start new iteration session
/imagegen:iterate --image base_image.png --prompt "Make it more vibrant"

# Continue existing session
/imagegen:iterate --session abc123 --prompt "Add more detail to the background"

# List active sessions
/imagegen:iterate --list
```

## Execution

For new session:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/iterate.py \
  --image "$ARGUMENTS.image" \
  --prompt "$ARGUMENTS.prompt"
```

For continuing session:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/iterate.py \
  --session "$ARGUMENTS.session" \
  --prompt "$ARGUMENTS.prompt"
```

For listing sessions:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/iterate.py --list
```

## Session Features

- **History tracking**: All steps are saved with prompts
- **Resume anytime**: Continue sessions later
- **Provider-specific**:
  - Google: True multi-turn conversation with image context
  - OpenAI: Edit-based iteration using last image

## Tips

- Start with a good base image
- Make incremental changes for best results
- Use descriptive prompts about what to change
- Check history to see what's been done: `--session ID --history`
