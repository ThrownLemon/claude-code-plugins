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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
import sys
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import get_output_dir
from providers import get_provider
from utils import format_size_for_openai, format_aspect_ratio_for_google, estimate_cost


def main():
    parser = argparse.ArgumentParser(description="Compare image generation providers")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--google-model", default="gemini-2.5-flash-image",
                        help="Google model")
    parser.add_argument("--openai-model", default="gpt-image-1",
                        help="OpenAI model")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--size", "-s", default="1:1", help="Size/aspect ratio")
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

    # Define generation tasks
    def generate_google():
        provider = get_provider("google", model=args.google_model)
        aspect_ratio = format_aspect_ratio_for_google(args.size)
        return provider.generate(args.prompt, google_output, aspect_ratio=aspect_ratio)

    def generate_openai():
        provider = get_provider("openai", model=args.openai_model)
        size = format_size_for_openai(args.size)
        return provider.generate(args.prompt, openai_output, size=size)

    # Generate in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(generate_google): "google",
            executor.submit(generate_openai): "openai"
        }

        for future in as_completed(futures):
            provider_name = futures[future]
            try:
                result = future.result()
                results[provider_name] = result.to_dict()

                if not args.json:
                    if result.success and result.files:
                        print(f"[OK] {provider_name.upper()}: {result.files[0]}")
                    elif result.success:
                        print(f"[OK] {provider_name.upper()}: (no output file)")
                    else:
                        print(f"[FAIL] {provider_name.upper()}: {result.error}")
            except Exception as e:
                results[provider_name] = {"success": False, "error": str(e)}
                if not args.json:
                    print(f"[FAIL] {provider_name.upper()}: {e}")

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
        success_count = sum(
            1 for r in [results["google"], results["openai"]]
            if r and r.get("success")
        )
        print(f"\nSuccess: {success_count}/2 providers")


if __name__ == "__main__":
    main()
