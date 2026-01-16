#!/usr/bin/env python3
"""
Image generation script supporting Google Gemini and OpenAI GPT-Image.

Usage:
    python generate.py --prompt "A cute cat" [options]

Options:
    --provider google|openai    Provider to use (default: from config)
    --model MODEL              Model to use (default: from config)
    --size SIZE                Image size/aspect ratio
    --quality low|medium|high  Quality level (OpenAI only)
    --output PATH              Output file path
    --count N                  Number of images to generate (1-4)
    --background transparent|opaque  Background type (OpenAI GPT-Image only)
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_output_dir
from providers import get_provider
from utils import (
    generate_filename, print_result, validate_api_key,
    format_size_for_openai, format_aspect_ratio_for_google, estimate_cost
)


def is_safe_output_path(output_path: Path) -> bool:
    """Validate output path to prevent directory traversal attacks."""
    try:
        resolved = output_path.resolve()
        # Don't allow writing to system directories
        dangerous_prefixes = ['/etc', '/usr', '/bin', '/sbin', '/var', '/root']
        for prefix in dangerous_prefixes:
            if str(resolved).startswith(prefix):
                return False
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate images with AI")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider to use")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--size", "-s", help="Size/aspect ratio")
    parser.add_argument("--quality", "-q", choices=["low", "medium", "high"],
                        default="high", help="Quality level (OpenAI only)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--count", "-n", type=int, default=1,
                        help="Number of images to generate")
    parser.add_argument("--background", "-b", choices=["transparent", "opaque", "auto"],
                        default="auto", help="Background type (OpenAI GPT-Image only)")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON")

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Determine provider
    provider_name = args.provider or config.get("default_provider", "google")

    # Validate API key
    valid, msg = validate_api_key(provider_name)
    if not valid:
        if args.json:
            print(json.dumps({"success": False, "error": msg}))
        else:
            print_result(False, msg)
        sys.exit(1)

    # Get provider-specific config
    provider_config = config.get(provider_name, {})

    # Determine model
    model = args.model or provider_config.get("model")

    # Get provider instance
    provider = get_provider(provider_name, model=model)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if not is_safe_output_path(output_path):
            error_msg = f"Unsafe output path: {args.output}"
            if args.json:
                print(json.dumps({"success": False, "error": error_msg}))
            else:
                print_result(False, error_msg)
            sys.exit(1)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = get_output_dir()
        filename = generate_filename(args.prompt)
        output_path = output_dir / filename

    # Build provider-specific kwargs
    if provider_name == "google":
        aspect_ratio = args.size or provider_config.get("aspect_ratio", "1:1")
        kwargs = {
            "aspect_ratio": format_aspect_ratio_for_google(aspect_ratio),
            "count": min(args.count, 4),  # Google supports up to 4
        }
    else:
        size = args.size or provider_config.get("size", "1024x1024")
        kwargs = {
            "size": format_size_for_openai(size),
            "quality": args.quality,
            "background": args.background,
            "count": args.count,
        }

    # Generate
    result = provider.generate(
        prompt=args.prompt,
        output_path=output_path,
        **kwargs
    )

    # Output result
    result_dict = result.to_dict()

    if args.json:
        print(json.dumps(result_dict, indent=2))
    else:
        if result.success:
            print_result(
                True,
                f"Generated {len(result.files)} image(s)",
                filepath=Path(result.files[0]) if result.files else None,
                metadata={
                    "provider": result.provider,
                    "model": result.model,
                    "files": result.files,
                    "estimated_cost": estimate_cost(provider_name, result.model, len(result.files))
                }
            )
        else:
            print_result(False, result.error or "Unknown error")
            sys.exit(1)


if __name__ == "__main__":
    main()
