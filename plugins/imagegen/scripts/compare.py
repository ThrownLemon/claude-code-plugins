#!/usr/bin/env python3
"""
Compare image generation between Google Gemini and OpenAI GPT-Image.
Generates the same prompt with both providers for side-by-side comparison.

Usage:
    python compare.py --prompt "A sunset over mountains" [options]

Options:
    --google-model MODEL     Google model to use
    --openai-model MODEL     OpenAI model to use
    --output-dir PATH        Output directory
    --size SIZE              Target size/aspect ratio
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
from utils import (
    generate_filename, save_base64_image, print_result,
    validate_api_key, format_size_for_openai, format_aspect_ratio_for_google,
    estimate_cost
)


def generate_google(prompt: str, model: str, aspect_ratio: str, output_path: Path) -> dict:
    """Generate with Google."""
    try:
        from google import genai
        from google.genai import types

        api_key = get_api_key("google")
        if not api_key:
            return {"success": False, "error": "Google API key not set", "provider": "google"}

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
                mime = getattr(part.inline_data, "mime_type", "image/png")
                ext = mime.split("/")[-1] if "/" in mime else "png"
                filepath = output_path.with_suffix(f".{ext}")

                with open(filepath, "wb") as f:
                    f.write(part.inline_data.data)

                return {
                    "success": True,
                    "file": str(filepath),
                    "provider": "google",
                    "model": model
                }

        return {"success": False, "error": "No image returned", "provider": "google"}

    except ImportError:
        return {"success": False, "error": "google-genai not installed", "provider": "google"}
    except Exception as e:
        return {"success": False, "error": str(e), "provider": "google"}


def generate_openai(prompt: str, model: str, size: str, output_path: Path) -> dict:
    """Generate with OpenAI."""
    try:
        from openai import OpenAI

        api_key = get_api_key("openai")
        if not api_key:
            return {"success": False, "error": "OpenAI API key not set", "provider": "openai"}

        client = OpenAI(api_key=api_key)

        params = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
        }
        if model.startswith("gpt-image"):
            params["quality"] = "high"

        response = client.images.generate(**params)

        if response.data:
            image_data = response.data[0]

            if hasattr(image_data, "b64_json") and image_data.b64_json:
                save_base64_image(image_data.b64_json, output_path)
                return {
                    "success": True,
                    "file": str(output_path),
                    "provider": "openai",
                    "model": model
                }
            elif hasattr(image_data, "url") and image_data.url:
                import urllib.request
                urllib.request.urlretrieve(image_data.url, output_path)
                return {
                    "success": True,
                    "file": str(output_path),
                    "provider": "openai",
                    "model": model
                }

        return {"success": False, "error": "No image returned", "provider": "openai"}

    except ImportError:
        return {"success": False, "error": "openai not installed", "provider": "openai"}
    except Exception as e:
        return {"success": False, "error": str(e), "provider": "openai"}


def main():
    parser = argparse.ArgumentParser(description="Compare image generation providers")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--google-model", default="gemini-2.5-flash-image",
                        help="Google model")
    parser.add_argument("--openai-model", default="gpt-image-1",
                        help="OpenAI model")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--size", "-s", default="1:1", help="Size/aspect ratio")
    parser.add_argument("--parallel", action="store_true", default=True,
                        help="Generate in parallel (default)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Setup output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = get_output_dir() / "comparisons"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for this comparison
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    google_output = output_dir / f"compare_{timestamp}_google.png"
    openai_output = output_dir / f"compare_{timestamp}_openai.png"

    # Format sizes
    aspect_ratio = format_aspect_ratio_for_google(args.size)
    openai_size = format_size_for_openai(args.size)

    results = {
        "prompt": args.prompt,
        "timestamp": timestamp,
        "google": None,
        "openai": None
    }

    if not args.json:
        print(f"Generating images for: \"{args.prompt[:50]}...\"")
        print(f"Google model: {args.google_model}")
        print(f"OpenAI model: {args.openai_model}")
        print()

    # Generate in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(
                generate_google, args.prompt, args.google_model, aspect_ratio, google_output
            ): "google",
            executor.submit(
                generate_openai, args.prompt, args.openai_model, openai_size, openai_output
            ): "openai"
        }

        for future in as_completed(futures):
            provider = futures[future]
            result = future.result()
            results[provider] = result

            if not args.json:
                if result["success"]:
                    print(f"[OK] {provider.upper()}: {result['file']}")
                else:
                    print(f"[FAIL] {provider.upper()}: {result['error']}")

    # Save comparison metadata
    meta_file = output_dir / f"compare_{timestamp}_meta.json"
    with open(meta_file, "w") as f:
        json.dump(results, f, indent=2)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print()
        print("Comparison complete!")
        print(f"Metadata saved to: {meta_file}")

        # Calculate costs
        google_cost = estimate_cost("google", args.google_model, 1)
        openai_cost = estimate_cost("openai", args.openai_model, 1)
        print(f"\nEstimated costs:")
        print(f"  Google ({args.google_model}): {google_cost}")
        print(f"  OpenAI ({args.openai_model}): {openai_cost}")

        # Summary
        success_count = sum(1 for r in [results["google"], results["openai"]] if r and r.get("success"))
        print(f"\nSuccess: {success_count}/2 providers")


if __name__ == "__main__":
    main()
