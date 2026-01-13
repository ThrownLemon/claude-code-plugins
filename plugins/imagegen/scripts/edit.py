#!/usr/bin/env python3
"""
Image editing script supporting Google Gemini (Gemini) and OpenAI GPT-Image.

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
import os
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_api_key, get_output_dir
from utils import (
    generate_filename, save_base64_image, load_image_as_base64,
    get_image_mime_type, print_result, validate_api_key,
    format_size_for_openai
)


def edit_with_google(image_path: Path, prompt: str, model: str,
                     output_path: Path) -> dict:
    """Edit image using Google Gemini API with multi-modal input."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {
            "success": False,
            "error": "google-genai package not installed. Run: pip install google-genai"
        }

    api_key = get_api_key("google")
    if not api_key:
        return {
            "success": False,
            "error": "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set"
        }

    try:
        client = genai.Client(api_key=api_key)

        # Load the image
        with open(image_path, "rb") as f:
            image_data = f.read()

        mime_type = get_image_mime_type(image_path)

        # Create image part
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=mime_type,
                data=image_data
            )
        )

        # Configure generation for image output
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )

        # Send both image and text prompt
        response = client.models.generate_content(
            model=model,
            contents=[image_part, prompt],
            config=config
        )

        # Extract and save edited image
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
                    "model": model,
                    "original": str(image_path),
                    "prompt": prompt
                }

        return {
            "success": False,
            "error": "No edited image returned from API"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def edit_with_openai(image_path: Path, prompt: str, model: str,
                     output_path: Path, mask_path: Path = None,
                     size: str = "1024x1024") -> dict:
    """Edit image using OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "success": False,
            "error": "openai package not installed. Run: pip install openai"
        }

    api_key = get_api_key("openai")
    if not api_key:
        return {
            "success": False,
            "error": "OPENAI_API_KEY environment variable not set"
        }

    try:
        client = OpenAI(api_key=api_key)

        # Use the edits endpoint with context manager
        with open(image_path, "rb") as image_file:
            response = client.images.edit(
                model=model,
                image=image_file,
                prompt=prompt,
                n=1,
                size=size
            )

        # Save the result
        if response.data:
            image_data = response.data[0]

            if hasattr(image_data, "b64_json") and image_data.b64_json:
                save_base64_image(image_data.b64_json, output_path)
            elif hasattr(image_data, "url") and image_data.url:
                import urllib.request
                urllib.request.urlretrieve(image_data.url, output_path)

            return {
                "success": True,
                "file": str(output_path),
                "provider": "openai",
                "model": model,
                "original": str(image_path),
                "prompt": prompt
            }

        return {
            "success": False,
            "error": "No edited image returned from API"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
    provider = args.provider or config.get("default_provider", "google")

    # Validate API key
    valid, msg = validate_api_key(provider)
    if not valid:
        if args.json:
            print(json.dumps({"success": False, "error": msg}))
        else:
            print_result(False, msg)
        sys.exit(1)

    # Get provider-specific config
    provider_config = config.get(provider, {})

    # Determine model
    model = args.model or provider_config.get("model")
    if not model:
        if provider == "google":
            model = "gemini-2.5-flash-image"
        else:
            model = "gpt-image-1"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = get_output_dir()
        # Use original filename with _edited suffix
        stem = image_path.stem
        filename = f"{stem}_edited.png"
        output_path = output_dir / filename

    # Edit based on provider
    if provider == "google":
        result = edit_with_google(
            image_path=image_path,
            prompt=args.prompt,
            model=model,
            output_path=output_path
        )
    else:
        mask_path = Path(args.mask) if args.mask else None
        size = format_size_for_openai(args.size)

        result = edit_with_openai(
            image_path=image_path,
            prompt=args.prompt,
            model=model,
            output_path=output_path,
            mask_path=mask_path,
            size=size
        )

    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print_result(
                True,
                "Image edited successfully",
                filepath=Path(result['file']),
                metadata={
                    "provider": result["provider"],
                    "model": result["model"],
                    "original": result["original"],
                    "edit_prompt": result["prompt"]
                }
            )
        else:
            print_result(False, result.get("error", "Unknown error"))
            sys.exit(1)


if __name__ == "__main__":
    main()
