---
name: imagegen
description: AI image generation using Google Gemini (Gemini) and OpenAI GPT-Image. Generate, edit, iterate, and create assets.
triggers:
  - "generate an image"
  - "create an image"
  - "make an image"
  - "draw"
  - "create a picture"
  - "generate a picture"
  - "create artwork"
  - "generate art"
  - "make me an image"
  - "create icons"
  - "generate icons"
  - "create a logo"
  - "generate a logo"
  - "create a moodboard"
  - "generate moodboard"
  - "design inspiration"
  - "character design"
  - "character sheet"
  - "edit this image"
  - "modify this image"
  - "change this image"
  - "update this image"
  - "refine this image"
  - "iterate on this"
  - "compare image providers"
  - "generate social images"
  - "create thumbnails"
  - "make favicons"
  - "dall-e"
  - "dalle"
  - "imagen"
  - "gemini image"
  - "gpt image"
---

# Image Generation Skill

This skill enables AI-powered image generation, editing, and asset creation using Google Gemini (Gemini) and OpenAI GPT-Image.

## When to Use

Activate this skill when the user wants to:
- Generate images from text descriptions
- Edit or modify existing images
- Create project assets (icons, favicons, social images)
- Generate design inspiration (moodboards)
- Create consistent character designs
- Compare different AI image providers

## Available Commands

| Command | Use For |
|---------|---------|
| `/imagegen:generate` | Generate images from prompts |
| `/imagegen:edit` | Edit existing images |
| `/imagegen:iterate` | Refine images through multiple steps |
| `/imagegen:compare` | Compare Google vs OpenAI |
| `/imagegen:assets` | Generate project assets |
| `/imagegen:moodboard` | Create design inspiration sets |
| `/imagegen:character` | Create consistent character sheets |
| `/imagegen:config` | Configure defaults |

## Delegation

For complex image generation tasks, delegate to the `image-generator` subagent which has access to all generation scripts and can handle multi-step workflows.

## Quick Reference

### Providers

**Google Gemini (Gemini)**
- Models: `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`
- Best for: Character consistency, multi-turn iteration, style variety
- API Key: `GEMINI_API_KEY` or `GOOGLE_API_KEY`

**OpenAI GPT-Image**
- Models: `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`
- Best for: Text in images, transparent backgrounds, precise edits
- API Key: `OPENAI_API_KEY`

### Common Sizes/Aspect Ratios

| Format | Google | OpenAI |
|--------|--------|--------|
| Square | 1:1 | 1024x1024 |
| Landscape | 16:9 | 1536x1024 |
| Portrait | 9:16 | 1024x1536 |
| Wide | 21:9 | - |

## Example Interactions

**User**: "Generate an image of a sunset over mountains"
**Action**: Use `/imagegen:generate --prompt "A sunset over mountains"`

**User**: "Create app icons for my project"
**Action**: Use `/imagegen:assets --type icons --prompt "[ask for description]"`

**User**: "Edit this image to add rain"
**Action**: Use `/imagegen:edit --image [path] --prompt "Add rain falling"`

**User**: "I want to iterate on this design"
**Action**: Use `/imagegen:iterate --image [path] --prompt "[refinement]"`

**User**: "Which provider would be better for logos?"
**Action**: Explain Google is better for style variety, OpenAI for text, and suggest `/imagegen:compare` to test both.

## Prerequisites Check

Before generating, verify:
1. Required Python packages: `google-genai`, `openai`, `Pillow` (for resizing)
2. API keys set in environment
3. Output directory accessible

```bash
# Install packages
pip install google-genai openai Pillow

# Set API keys (user's responsibility)
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

## Prompt Tips

Help users craft effective prompts:
- Be descriptive but concise
- Specify style (photorealistic, watercolor, minimalist)
- Include lighting (golden hour, dramatic, soft)
- Mention composition (close-up, wide shot, centered)
- For characters, include distinctive features
- For logos, specify simplicity level
