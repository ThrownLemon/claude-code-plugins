#!/usr/bin/env python3
"""
Image generation script supporting Google Gemini (Gemini) and OpenAI GPT-Image.

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
import ipaddress
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_api_key, get_output_dir
from utils import (
    generate_filename, save_base64_image, print_result,
    validate_api_key, parse_provider_model, format_size_for_openai,
    format_aspect_ratio_for_google, estimate_cost
)


def is_safe_output_path(output_path: Path, base_dir: Path = None) -> bool:
    """Validate output path to prevent directory traversal attacks.

    Args:
        output_path: The path to validate.
        base_dir: If provided, ensure output is within this directory.

    Returns:
        True if safe, False otherwise.
    """
    try:
        resolved = output_path.resolve()

        # Don't allow writing to system directories
        dangerous_prefixes = ['/etc', '/usr', '/bin', '/sbin', '/var', '/root']
        for prefix in dangerous_prefixes:
            if str(resolved).startswith(prefix):
                return False

        # If base_dir specified, ensure output is within it
        if base_dir:
            base_resolved = base_dir.resolve()
            if not str(resolved).startswith(str(base_resolved)):
                return False

        return True
    except Exception:
        return False


def is_safe_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks.

    Rejects private IP ranges, localhost, and cloud metadata endpoints.
    Returns True if URL is safe to fetch, False otherwise.
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname

        if not host:
            return False

        # Check for localhost variants
        if host in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            return False

        # Check for cloud metadata endpoints
        if host in ('169.254.169.254', 'metadata.google.internal',
                    'metadata.google.com'):
            return False

        # Try to parse as IP address and check for private ranges
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # Not an IP address, hostname is fine
            pass

        return True
    except Exception:
        return False


def generate_with_google(prompt: str, model: str, aspect_ratio: str,
                         output_path: Path, count: int = 1) -> dict:
    """Generate image using Google Gemini API."""
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

        # Configure generation
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )

        # Add aspect ratio if supported
        if aspect_ratio:
            config.image_config = types.ImageConfig(aspect_ratio=aspect_ratio)

        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=config
        )

        # Extract and save image(s)
        saved_files = []
        for i, part in enumerate(response.parts):
            if hasattr(part, "inline_data") and part.inline_data:
                # Determine file extension from mime type
                mime = getattr(part.inline_data, "mime_type", "image/png")
                ext = mime.split("/")[-1] if "/" in mime else "png"

                # Generate filename
                if count > 1:
                    filepath = output_path.parent / f"{output_path.stem}_{i+1}.{ext}"
                else:
                    filepath = output_path.with_suffix(f".{ext}")

                # Save the image
                image_data = part.inline_data.data
                with open(filepath, "wb") as f:
                    f.write(image_data)
                saved_files.append(str(filepath))

        if saved_files:
            return {
                "success": True,
                "files": saved_files,
                "provider": "google",
                "model": model,
                "prompt": prompt
            }
        else:
            return {
                "success": False,
                "error": "No images returned from API"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_with_openai(prompt: str, model: str, size: str,
                         quality: str, output_path: Path,
                         count: int = 1, background: str = "auto") -> dict:
    """Generate image using OpenAI GPT-Image API."""
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

        # Build request parameters
        params = {
            "model": model,
            "prompt": prompt,
            "n": min(count, 10),  # OpenAI allows up to 10
            "size": size,
        }

        # GPT-Image specific parameters
        if model.startswith("gpt-image"):
            params["quality"] = quality
            if background != "auto":
                params["background"] = background

        response = client.images.generate(**params)

        # Save images
        saved_files = []
        for i, image_data in enumerate(response.data):
            # Generate filename
            if count > 1:
                filepath = output_path.parent / f"{output_path.stem}_{i+1}.png"
            else:
                filepath = output_path

            # GPT-Image returns base64
            if hasattr(image_data, "b64_json") and image_data.b64_json:
                save_base64_image(image_data.b64_json, filepath)
                saved_files.append(str(filepath))
            # DALL-E may return URL
            elif hasattr(image_data, "url") and image_data.url:
                # Validate URL before downloading (defense in depth)
                if not is_safe_url(image_data.url):
                    return {
                        "success": False,
                        "error": f"Unsafe URL returned by API: {image_data.url}"
                    }
                import urllib.request
                urllib.request.urlretrieve(image_data.url, filepath)
                saved_files.append(str(filepath))

        if saved_files:
            return {
                "success": True,
                "files": saved_files,
                "provider": "openai",
                "model": model,
                "prompt": prompt
            }
        else:
            return {
                "success": False,
                "error": "No images returned from API"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
        # Validate output path to prevent directory traversal
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

    # Generate based on provider
    if provider == "google":
        aspect_ratio = args.size or provider_config.get("aspect_ratio", "1:1")
        aspect_ratio = format_aspect_ratio_for_google(aspect_ratio)

        result = generate_with_google(
            prompt=args.prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            output_path=output_path,
            count=min(args.count, 4)  # Google supports up to 4
        )
    else:
        size = args.size or provider_config.get("size", "1024x1024")
        size = format_size_for_openai(size)

        result = generate_with_openai(
            prompt=args.prompt,
            model=model,
            size=size,
            quality=args.quality,
            output_path=output_path,
            count=args.count,
            background=args.background
        )

    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print_result(
                True,
                f"Generated {len(result['files'])} image(s)",
                filepath=Path(result['files'][0]) if result['files'] else None,
                metadata={
                    "provider": result["provider"],
                    "model": result["model"],
                    "files": result["files"],
                    "estimated_cost": estimate_cost(provider, model, len(result['files']))
                }
            )
        else:
            print_result(False, result.get("error", "Unknown error"))
            sys.exit(1)


if __name__ == "__main__":
    main()
