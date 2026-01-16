#!/usr/bin/env python3
"""
Image editing script supporting Google Gemini and OpenAI GPT-Image.

Usage:
    python edit.py --image PATH --prompt "Edit instructions" [options]

Options:
    --provider google|openai    Provider to use (default: from config)
    --model MODEL              Model to use (default: from config)
    --mask PATH                Mask image for inpainting (OpenAI)
    --output PATH              Output file path
    --size SIZE                Output size (OpenAI only)
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
from utils import print_result, validate_api_key, format_size_for_openai


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
    parser = argparse.ArgumentParser(description="Edit images with AI")
    parser.add_argument("--image", "-i", required=True, help="Input image path")
    parser.add_argument("--prompt", "-p", required=True, help="Edit instructions")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider to use")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--mask", help="Mask image for inpainting (OpenAI)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--size", "-s", default="1024x1024",
                        help="Output size (OpenAI only)")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON")

    args = parser.parse_args()

    # Validate input image exists
    image_path = Path(args.image)
    if not image_path.exists():
        error_msg = f"Input image not found: {args.image}"
        if args.json:
            print(json.dumps({"success": False, "error": error_msg}))
        else:
            print_result(False, error_msg)
        sys.exit(1)

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
        filename = f"{image_path.stem}_edited.png"
        output_path = output_dir / filename

    # Build provider-specific kwargs
    kwargs = {}
    if provider_name == "openai":
        kwargs["size"] = format_size_for_openai(args.size)
        if args.mask:
            kwargs["mask_path"] = Path(args.mask)

    # Edit
    result = provider.edit(
        image_path=image_path,
        prompt=args.prompt,
        output_path=output_path,
        **kwargs
    )

    # Output result
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print_result(
                True,
                "Image edited successfully",
                filepath=Path(result.files[0]) if result.files else None,
                metadata={
                    "provider": result.provider,
                    "model": result.model,
                    "original": str(image_path),
                    "edit_prompt": args.prompt
                }
            )
        else:
            print_result(False, result.error or "Unknown error")
            sys.exit(1)


if __name__ == "__main__":
    main()
