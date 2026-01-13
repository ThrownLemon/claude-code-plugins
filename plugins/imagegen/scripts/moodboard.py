#!/usr/bin/env python3
"""
Moodboard generator - creates multiple related images for design inspiration.

Usage:
    python moodboard.py --theme "Cyberpunk city" [options]
    python moodboard.py --theme "Cozy coffee shop" --style "watercolor"
    python moodboard.py --theme "Tech startup" --variations 6

Options:
    --theme THEME           Main theme/concept for the moodboard
    --style STYLE           Artistic style (realistic, watercolor, minimal, etc.)
    --variations N          Number of variations to generate (default: 4)
    --aspects               Generate with different aspect ratios
    --provider PROVIDER     Provider to use
    --output-dir PATH       Output directory
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_api_key, get_output_dir
from utils import print_result, validate_api_key, generate_filename

# Style modifiers for variety
STYLE_MODIFIERS = {
    "realistic": "photorealistic, detailed, high resolution",
    "watercolor": "watercolor painting style, soft edges, artistic",
    "minimal": "minimalist design, clean lines, simple composition",
    "vintage": "vintage aesthetic, retro colors, nostalgic feel",
    "neon": "neon colors, glowing effects, vibrant",
    "pastel": "soft pastel colors, gentle tones, dreamy",
    "dark": "dark moody atmosphere, dramatic lighting, cinematic",
    "bright": "bright and cheerful, high key lighting, optimistic",
    "abstract": "abstract interpretation, artistic, conceptual",
    "sketch": "pencil sketch style, hand-drawn look, artistic",
    "3d": "3D rendered, volumetric lighting, modern",
    "flat": "flat design, bold colors, graphic style"
}

# Variation prompts to add diversity
VARIATION_ANGLES = [
    "wide establishing shot",
    "close-up detail",
    "from above, bird's eye view",
    "dynamic angle",
    "soft focus background",
    "dramatic lighting",
    "golden hour lighting",
    "moody atmosphere",
    "vibrant and energetic",
    "calm and serene"
]

ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3"]


def generate_image(prompt: str, provider: str, model: str,
                   aspect_ratio: str, output_path: Path) -> dict:
    """Generate a single image."""
    if provider == "google":
        try:
            from google import genai
            from google.genai import types

            api_key = get_api_key("google")
            client = genai.Client(api_key=api_key)

            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
            if aspect_ratio:
                config.image_config = types.ImageConfig(aspect_ratio=aspect_ratio)

            response = client.models.generate_content(
                model=model,
                contents=[prompt],
                config=config
            )

            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    return {"success": True, "file": str(output_path), "prompt": prompt}

            return {"success": False, "error": "No image returned", "prompt": prompt}

        except Exception as e:
            return {"success": False, "error": str(e), "prompt": prompt}

    else:  # openai
        try:
            from openai import OpenAI
            from utils import save_base64_image

            api_key = get_api_key("openai")
            client = OpenAI(api_key=api_key)

            size_map = {"1:1": "1024x1024", "16:9": "1536x1024", "9:16": "1024x1536", "4:3": "1024x1024"}
            size = size_map.get(aspect_ratio, "1024x1024")

            response = client.images.generate(
                model=model,
                prompt=prompt,
                n=1,
                size=size,
                quality="high"
            )

            if response.data:
                image_data = response.data[0]
                if hasattr(image_data, "b64_json") and image_data.b64_json:
                    save_base64_image(image_data.b64_json, output_path)
                    return {"success": True, "file": str(output_path), "prompt": prompt}

            return {"success": False, "error": "No image returned", "prompt": prompt}

        except Exception as e:
            return {"success": False, "error": str(e), "prompt": prompt}


def create_variation_prompts(theme: str, style: str, count: int,
                             use_aspects: bool = False) -> list:
    """Create diverse prompts for moodboard."""
    prompts = []

    style_mod = STYLE_MODIFIERS.get(style, style) if style else ""

    for i in range(count):
        # Cycle through variation angles
        angle = VARIATION_ANGLES[i % len(VARIATION_ANGLES)]

        # Build prompt
        parts = [theme]
        if style_mod:
            parts.append(style_mod)
        parts.append(angle)

        prompt = ", ".join(parts)

        # Determine aspect ratio
        if use_aspects:
            aspect = ASPECT_RATIOS[i % len(ASPECT_RATIOS)]
        else:
            aspect = "1:1"

        prompts.append({
            "prompt": prompt,
            "aspect_ratio": aspect,
            "index": i + 1
        })

    return prompts


def main():
    parser = argparse.ArgumentParser(description="Generate moodboard images")
    parser.add_argument("--theme", "-t", required=True, help="Main theme/concept")
    parser.add_argument("--style", "-s", help="Artistic style",
                        choices=list(STYLE_MODIFIERS.keys()) + ["custom"])
    parser.add_argument("--custom-style", help="Custom style description")
    parser.add_argument("--variations", "-n", type=int, default=4,
                        help="Number of variations (default: 4)")
    parser.add_argument("--aspects", action="store_true",
                        help="Use different aspect ratios")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider to use")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--parallel", type=int, default=2,
                        help="Parallel generation threads (default: 2)")
    parser.add_argument("--list-styles", action="store_true",
                        help="List available styles")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # List styles
    if args.list_styles:
        print("Available styles:")
        for name, desc in STYLE_MODIFIERS.items():
            print(f"  {name}: {desc}")
        return

    # Load config
    config = load_config()
    provider = args.provider or config.get("default_provider", "google")

    # Validate API key
    valid, msg = validate_api_key(provider)
    if not valid:
        if args.json:
            print(json.dumps({"success": False, "error": msg}))
        else:
            print_result(False, msg)
        sys.exit(1)

    # Get model
    provider_config = config.get(provider, {})
    model = args.model or provider_config.get("model")
    if not model:
        model = "gemini-2.5-flash-image" if provider == "google" else "gpt-image-1"

    # Handle custom style
    style = args.custom_style if args.style == "custom" else args.style

    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Create themed directory
        theme_slug = args.theme.lower().replace(" ", "_")[:30]
        output_dir = get_output_dir() / "moodboards" / f"{theme_slug}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create variation prompts
    variations = create_variation_prompts(
        theme=args.theme,
        style=style,
        count=args.variations,
        use_aspects=args.aspects
    )

    if not args.json:
        print(f"Generating moodboard: \"{args.theme}\"")
        print(f"Style: {style or 'default'}")
        print(f"Variations: {len(variations)}")
        print(f"Provider: {provider} ({model})")
        print(f"Output: {output_dir}")
        print()

    results = {
        "theme": args.theme,
        "style": style,
        "provider": provider,
        "model": model,
        "files": [],
        "errors": []
    }

    # Generate images in parallel
    def generate_variation(var):
        output_path = output_dir / f"moodboard_{var['index']:02d}.png"
        return generate_image(
            prompt=var["prompt"],
            provider=provider,
            model=model,
            aspect_ratio=var["aspect_ratio"],
            output_path=output_path
        )

    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {executor.submit(generate_variation, v): v for v in variations}

        for future in as_completed(futures):
            var = futures[future]
            result = future.result()

            if result["success"]:
                results["files"].append({
                    "file": result["file"],
                    "prompt": result["prompt"],
                    "index": var["index"]
                })
                if not args.json:
                    print(f"[{var['index']}/{len(variations)}] Generated: {result['file']}")
            else:
                results["errors"].append({
                    "index": var["index"],
                    "error": result["error"]
                })
                if not args.json:
                    print(f"[{var['index']}/{len(variations)}] Failed: {result['error']}")

    # Save metadata
    meta_file = output_dir / "moodboard_meta.json"
    with open(meta_file, "w") as f:
        json.dump({
            "theme": args.theme,
            "style": style,
            "provider": provider,
            "model": model,
            "variations": variations,
            "files": [f["file"] for f in results["files"]]
        }, f, indent=2)

    results["success"] = len(results["files"]) > 0
    results["metadata_file"] = str(meta_file)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print()
        if results["success"]:
            print_result(
                True,
                f"Generated {len(results['files'])}/{len(variations)} images",
                metadata={
                    "output_dir": str(output_dir),
                    "metadata": str(meta_file)
                }
            )
        else:
            print_result(False, "Moodboard generation failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
