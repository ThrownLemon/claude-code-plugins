#!/usr/bin/env python3
"""
Asset pipeline for generating app icons, social banners, and other project assets.

Usage:
    python assets.py --type icons --prompt "A minimalist owl logo" [options]
    python assets.py --type social --prompt "Tech blog header" [options]
    python assets.py --type favicons --prompt "Letter T in blue circle"

Asset Types:
    icons      - App icons in multiple sizes (16, 32, 48, 64, 128, 256, 512, 1024)
    favicons   - Web favicons (16, 32, 48, 180, 192, 512)
    social     - Social media images (og, twitter, linkedin, instagram)
    thumbnails - Video/content thumbnails (various aspect ratios)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_api_key, get_output_dir
from utils import print_result, validate_api_key, get_image_mime_type

# Asset type definitions
ASSET_TYPES = {
    "icons": {
        "description": "App icons for iOS, Android, macOS, Windows",
        "sizes": [16, 32, 48, 64, 128, 256, 512, 1024],
        "aspect_ratio": "1:1",
        "naming": "icon_{size}.png"
    },
    "favicons": {
        "description": "Web favicons and touch icons",
        "sizes": [16, 32, 48, 180, 192, 512],
        "aspect_ratio": "1:1",
        "naming": "favicon_{size}.png",
        "extras": ["favicon.ico", "apple-touch-icon.png"]
    },
    "social": {
        "description": "Social media images",
        "variants": {
            "og": {"width": 1200, "height": 630, "aspect": "16:9", "name": "og-image.png"},
            "twitter": {"width": 1200, "height": 628, "aspect": "16:9", "name": "twitter-card.png"},
            "linkedin": {"width": 1200, "height": 627, "aspect": "16:9", "name": "linkedin-banner.png"},
            "instagram": {"width": 1080, "height": 1080, "aspect": "1:1", "name": "instagram-post.png"},
            "instagram_story": {"width": 1080, "height": 1920, "aspect": "9:16", "name": "instagram-story.png"}
        }
    },
    "thumbnails": {
        "description": "Content thumbnails",
        "variants": {
            "youtube": {"width": 1280, "height": 720, "aspect": "16:9", "name": "youtube-thumb.png"},
            "vimeo": {"width": 1280, "height": 720, "aspect": "16:9", "name": "vimeo-thumb.png"},
            "blog": {"width": 800, "height": 450, "aspect": "16:9", "name": "blog-thumb.png"},
            "square": {"width": 800, "height": 800, "aspect": "1:1", "name": "square-thumb.png"}
        }
    }
}


def generate_base_image(prompt: str, provider: str, model: str,
                        aspect_ratio: str, output_path: Path) -> dict:
    """Generate a base image at high resolution."""
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
                    return {"success": True, "file": str(output_path)}

            return {"success": False, "error": "No image returned"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    else:  # openai
        try:
            from openai import OpenAI
            from utils import save_base64_image

            api_key = get_api_key("openai")
            client = OpenAI(api_key=api_key)

            # Map aspect ratio to OpenAI size
            size_map = {
                "1:1": "1024x1024",
                "16:9": "1536x1024",
                "9:16": "1024x1536"
            }
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
                    return {"success": True, "file": str(output_path)}

            return {"success": False, "error": "No image returned"}

        except Exception as e:
            return {"success": False, "error": str(e)}


def resize_image(input_path: Path, output_path: Path, width: int, height: int = None) -> bool:
    """Resize image using PIL."""
    try:
        from PIL import Image

        with Image.open(input_path) as img:
            if height is None:
                height = width  # Square

            # Use high-quality resampling
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(output_path, quality=95)
            return True

    except ImportError:
        print("Warning: PIL not available for resizing. Install: pip install Pillow")
        return False
    except Exception as e:
        print(f"Resize error: {e}")
        return False


def create_ico(png_files: List[Path], output_path: Path) -> bool:
    """Create .ico file from PNG files."""
    try:
        from PIL import Image

        images = []
        for png_file in png_files:
            if png_file.exists():
                with Image.open(png_file) as img:
                    images.append(img.copy())

        if images:
            images[0].save(output_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
            return True
        return False

    except Exception as e:
        print(f"ICO creation error: {e}")
        return False


def generate_icons(prompt: str, provider: str, model: str, output_dir: Path) -> dict:
    """Generate app icons at multiple sizes."""
    asset_config = ASSET_TYPES["icons"]
    results = {"type": "icons", "files": [], "errors": []}

    # Generate base image at highest resolution
    base_path = output_dir / "icon_base.png"
    base_result = generate_base_image(
        prompt=f"{prompt}. Simple, clean icon design, centered, suitable for app icon.",
        provider=provider,
        model=model,
        aspect_ratio="1:1",
        output_path=base_path
    )

    if not base_result["success"]:
        return {"success": False, "error": base_result["error"]}

    results["files"].append(str(base_path))

    # Resize to all sizes
    for size in asset_config["sizes"]:
        output_path = output_dir / f"icon_{size}.png"
        if resize_image(base_path, output_path, size, size):
            results["files"].append(str(output_path))
        else:
            results["errors"].append(f"Failed to resize to {size}x{size}")

    results["success"] = len(results["files"]) > 1
    return results


def generate_favicons(prompt: str, provider: str, model: str, output_dir: Path) -> dict:
    """Generate web favicons."""
    asset_config = ASSET_TYPES["favicons"]
    results = {"type": "favicons", "files": [], "errors": []}

    # Generate base image
    base_path = output_dir / "favicon_base.png"
    base_result = generate_base_image(
        prompt=f"{prompt}. Simple favicon design, high contrast, recognizable at small sizes.",
        provider=provider,
        model=model,
        aspect_ratio="1:1",
        output_path=base_path
    )

    if not base_result["success"]:
        return {"success": False, "error": base_result["error"]}

    results["files"].append(str(base_path))

    # Resize to all sizes
    png_files = []
    for size in asset_config["sizes"]:
        output_path = output_dir / f"favicon-{size}x{size}.png"
        if resize_image(base_path, output_path, size, size):
            results["files"].append(str(output_path))
            png_files.append(output_path)

    # Create favicon.ico
    ico_path = output_dir / "favicon.ico"
    if create_ico(png_files[:3], ico_path):  # Use 16, 32, 48
        results["files"].append(str(ico_path))

    # Create apple-touch-icon
    apple_path = output_dir / "apple-touch-icon.png"
    if resize_image(base_path, apple_path, 180, 180):
        results["files"].append(str(apple_path))

    results["success"] = len(results["files"]) > 1
    return results


def generate_social(prompt: str, provider: str, model: str, output_dir: Path,
                    variants: List[str] = None) -> dict:
    """Generate social media images."""
    asset_config = ASSET_TYPES["social"]
    results = {"type": "social", "files": [], "errors": []}

    if variants is None:
        variants = list(asset_config["variants"].keys())

    for variant_name in variants:
        if variant_name not in asset_config["variants"]:
            results["errors"].append(f"Unknown variant: {variant_name}")
            continue

        variant = asset_config["variants"][variant_name]
        output_path = output_dir / variant["name"]

        # Generate with appropriate aspect ratio
        result = generate_base_image(
            prompt=f"{prompt}. Optimized for {variant_name} ({variant['width']}x{variant['height']}).",
            provider=provider,
            model=model,
            aspect_ratio=variant["aspect"],
            output_path=output_path
        )

        if result["success"]:
            results["files"].append(str(output_path))
        else:
            results["errors"].append(f"{variant_name}: {result['error']}")

    results["success"] = len(results["files"]) > 0
    return results


def generate_thumbnails(prompt: str, provider: str, model: str, output_dir: Path,
                        variants: List[str] = None) -> dict:
    """Generate content thumbnails."""
    asset_config = ASSET_TYPES["thumbnails"]
    results = {"type": "thumbnails", "files": [], "errors": []}

    if variants is None:
        variants = list(asset_config["variants"].keys())

    for variant_name in variants:
        if variant_name not in asset_config["variants"]:
            results["errors"].append(f"Unknown variant: {variant_name}")
            continue

        variant = asset_config["variants"][variant_name]
        output_path = output_dir / variant["name"]

        result = generate_base_image(
            prompt=f"{prompt}. Eye-catching thumbnail, clear subject, good for {variant_name}.",
            provider=provider,
            model=model,
            aspect_ratio=variant["aspect"],
            output_path=output_path
        )

        if result["success"]:
            results["files"].append(str(output_path))
        else:
            results["errors"].append(f"{variant_name}: {result['error']}")

    results["success"] = len(results["files"]) > 0
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate project assets")
    parser.add_argument("--type", "-t", required=True,
                        choices=["icons", "favicons", "social", "thumbnails"],
                        help="Asset type to generate")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider to use")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--variants", nargs="+",
                        help="Specific variants (for social/thumbnails)")
    parser.add_argument("--list-variants", action="store_true",
                        help="List available variants for asset type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # List variants
    if args.list_variants:
        asset_config = ASSET_TYPES.get(args.type)
        if asset_config:
            print(f"Asset type: {args.type}")
            print(f"Description: {asset_config['description']}")
            if "sizes" in asset_config:
                print(f"Sizes: {asset_config['sizes']}")
            if "variants" in asset_config:
                print("Variants:")
                for name, v in asset_config["variants"].items():
                    print(f"  {name}: {v['width']}x{v['height']} ({v['aspect']})")
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

    # Setup output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = get_output_dir() / "assets" / args.type
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.json:
        print(f"Generating {args.type} assets...")
        print(f"Provider: {provider} ({model})")
        print(f"Output: {output_dir}")
        print()

    # Generate based on type
    if args.type == "icons":
        result = generate_icons(args.prompt, provider, model, output_dir)
    elif args.type == "favicons":
        result = generate_favicons(args.prompt, provider, model, output_dir)
    elif args.type == "social":
        result = generate_social(args.prompt, provider, model, output_dir, args.variants)
    elif args.type == "thumbnails":
        result = generate_thumbnails(args.prompt, provider, model, output_dir, args.variants)

    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print_result(
                True,
                f"Generated {len(result['files'])} files",
                metadata={
                    "type": result["type"],
                    "files": result["files"],
                    "errors": result.get("errors", [])
                }
            )
        else:
            print_result(False, result.get("error", "Generation failed"))
            if result.get("errors"):
                for err in result["errors"]:
                    print(f"  - {err}")
            sys.exit(1)


if __name__ == "__main__":
    main()
