#!/usr/bin/env python3
"""
Character sheet generator - creates consistent character designs across multiple poses/views.
Leverages Gemini's character consistency features for best results.

Usage:
    python character.py --description "A young wizard with blue robes" [options]
    python character.py --description "Robot companion" --poses "front,side,action"
    python character.py --reference IMAGE --description "Same character but older"

Options:
    --description DESC      Character description
    --reference IMAGE       Reference image for character consistency
    --poses POSES           Comma-separated poses to generate
    --style STYLE           Art style (anime, realistic, cartoon, etc.)
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
from utils import print_result, validate_api_key, get_image_mime_type

# Predefined pose sets
POSE_PRESETS = {
    "standard": ["front view", "three-quarter view", "side profile", "back view"],
    "action": ["standing pose", "running pose", "jumping pose", "sitting pose"],
    "expressions": ["neutral expression", "happy expression", "angry expression", "sad expression"],
    "turnaround": ["front view", "three-quarter left", "side left", "three-quarter back", "back view"],
    "headshots": ["front face", "three-quarter face", "profile face", "looking up", "looking down"]
}

# Art style modifiers
STYLE_MODIFIERS = {
    "anime": "anime style, cel shaded, vibrant colors",
    "realistic": "photorealistic, detailed, lifelike",
    "cartoon": "cartoon style, bold outlines, exaggerated features",
    "pixel": "pixel art style, retro gaming aesthetic",
    "watercolor": "watercolor illustration, soft edges, artistic",
    "comic": "comic book style, dynamic lines, bold colors",
    "chibi": "chibi style, cute, big head small body",
    "concept": "concept art style, professional, detailed design",
    "3d": "3D rendered, volumetric lighting, stylized",
    "sketch": "pencil sketch, hand-drawn, artistic"
}


def generate_with_reference(description: str, pose: str, reference_path: Path,
                            style: str, provider: str, model: str,
                            output_path: Path) -> dict:
    """Generate character image with reference for consistency."""
    if provider == "google":
        try:
            from google import genai
            from google.genai import types

            api_key = get_api_key("google")
            client = genai.Client(api_key=api_key)

            # Build prompt
            style_mod = STYLE_MODIFIERS.get(style, style) if style else ""
            prompt_parts = [
                f"Character: {description}",
                f"Pose: {pose}",
                "Maintain exact character design and features from reference image"
            ]
            if style_mod:
                prompt_parts.append(f"Style: {style_mod}")
            prompt = ". ".join(prompt_parts)

            # Load reference image
            contents = []
            if reference_path and reference_path.exists():
                with open(reference_path, "rb") as f:
                    image_data = f.read()
                mime_type = get_image_mime_type(reference_path)

                contents.append(types.Part(
                    inline_data=types.Blob(
                        mime_type=mime_type,
                        data=image_data
                    )
                ))

            contents.append(prompt)

            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    return {
                        "success": True,
                        "file": str(output_path),
                        "pose": pose
                    }

            return {"success": False, "error": "No image returned", "pose": pose}

        except Exception as e:
            return {"success": False, "error": str(e), "pose": pose}

    else:  # OpenAI - less ideal for character consistency but still works
        try:
            from openai import OpenAI
            from utils import save_base64_image

            api_key = get_api_key("openai")
            client = OpenAI(api_key=api_key)

            style_mod = STYLE_MODIFIERS.get(style, style) if style else ""
            prompt_parts = [f"Character design: {description}", f"Pose: {pose}"]
            if style_mod:
                prompt_parts.append(style_mod)

            # If we have a reference, use edit endpoint
            if reference_path and reference_path.exists():
                with open(reference_path, "rb") as ref_file:
                    response = client.images.edit(
                        model=model,
                        image=ref_file,
                        prompt=". ".join(prompt_parts),
                        n=1,
                        size="1024x1024"
                    )
            else:
                response = client.images.generate(
                    model=model,
                    prompt=". ".join(prompt_parts),
                    n=1,
                    size="1024x1024",
                    quality="high"
                )

            if response.data:
                image_data = response.data[0]
                if hasattr(image_data, "b64_json") and image_data.b64_json:
                    save_base64_image(image_data.b64_json, output_path)
                    return {"success": True, "file": str(output_path), "pose": pose}

            return {"success": False, "error": "No image returned", "pose": pose}

        except Exception as e:
            return {"success": False, "error": str(e), "pose": pose}


def generate_character_sheet(description: str, poses: list, style: str,
                             provider: str, model: str, output_dir: Path,
                             reference_path: Path = None, parallel: int = 2,
                             quiet: bool = False) -> dict:
    """Generate complete character sheet with multiple poses."""
    results = {
        "description": description,
        "style": style,
        "poses": poses,
        "files": [],
        "errors": []
    }

    # For consistent characters, generate first image then use as reference
    first_pose = poses[0]
    first_output = output_dir / f"character_01_{first_pose.replace(' ', '_')}.png"

    if not quiet:
        print(f"Generating base character: {first_pose}")

    first_result = generate_with_reference(
        description=description,
        pose=first_pose,
        reference_path=reference_path,
        style=style,
        provider=provider,
        model=model,
        output_path=first_output
    )

    if first_result["success"]:
        results["files"].append({
            "file": first_result["file"],
            "pose": first_pose,
            "index": 1
        })
        # Use this as reference for remaining poses
        reference_for_remaining = Path(first_result["file"])
    else:
        results["errors"].append({"pose": first_pose, "error": first_result["error"]})
        # Continue without reference
        reference_for_remaining = reference_path

    # Generate remaining poses
    remaining_poses = poses[1:]
    if remaining_poses:
        def generate_pose(pose_info):
            idx, pose = pose_info
            output_path = output_dir / f"character_{idx:02d}_{pose.replace(' ', '_')}.png"
            return generate_with_reference(
                description=description,
                pose=pose,
                reference_path=reference_for_remaining,
                style=style,
                provider=provider,
                model=model,
                output_path=output_path
            ), idx

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(generate_pose, (i + 2, pose)): pose
                for i, pose in enumerate(remaining_poses)
            }

            for future in as_completed(futures):
                pose = futures[future]
                result, idx = future.result()

                if result["success"]:
                    results["files"].append({
                        "file": result["file"],
                        "pose": pose,
                        "index": idx
                    })
                    if not quiet:
                        print(f"[{idx}/{len(poses)}] Generated: {pose}")
                else:
                    results["errors"].append({"pose": pose, "error": result["error"]})
                    if not quiet:
                        print(f"[{idx}/{len(poses)}] Failed: {pose} - {result['error']}")

    results["success"] = len(results["files"]) > 0
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate character sheets")
    parser.add_argument("--description", "-d", required=True,
                        help="Character description")
    parser.add_argument("--reference", "-r", help="Reference image path")
    parser.add_argument("--poses", "-p",
                        help="Comma-separated poses or preset name")
    parser.add_argument("--style", "-s",
                        help="Art style (anime, realistic, cartoon, etc.)")
    parser.add_argument("--provider", choices=["google", "openai"],
                        help="Provider (google recommended for consistency)")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--parallel", type=int, default=2,
                        help="Parallel generation threads")
    parser.add_argument("--list-presets", action="store_true",
                        help="List pose presets")
    parser.add_argument("--list-styles", action="store_true",
                        help="List available styles")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # List presets
    if args.list_presets:
        print("Available pose presets:")
        for name, poses in POSE_PRESETS.items():
            print(f"  {name}: {', '.join(poses)}")
        return

    # List styles
    if args.list_styles:
        print("Available styles:")
        for name, desc in STYLE_MODIFIERS.items():
            print(f"  {name}: {desc}")
        return

    # Parse poses
    if args.poses:
        if args.poses in POSE_PRESETS:
            poses = POSE_PRESETS[args.poses]
        else:
            poses = [p.strip() for p in args.poses.split(",")]
    else:
        poses = POSE_PRESETS["standard"]

    # Load config
    config = load_config()
    provider = args.provider or config.get("default_provider", "google")

    # Recommend Google for character consistency
    if provider != "google" and not args.json:
        print("Note: Google Gemini is recommended for character consistency.")
        print("Use --provider google for best results.")
        print()

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
        # Use better model for character consistency
        if provider == "google":
            model = "gemini-3-pro-image-preview"  # Better for consistency
        else:
            model = "gpt-image-1"

    # Reference image
    reference_path = Path(args.reference) if args.reference else None
    if reference_path and not reference_path.exists():
        error_msg = f"Reference image not found: {args.reference}"
        if args.json:
            print(json.dumps({"success": False, "error": error_msg}))
        else:
            print_result(False, error_msg)
        sys.exit(1)

    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        desc_slug = args.description.lower().replace(" ", "_")[:20]
        output_dir = get_output_dir() / "characters" / f"{desc_slug}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.json:
        print(f"Generating character sheet: \"{args.description[:50]}...\"")
        print(f"Style: {args.style or 'default'}")
        print(f"Poses: {', '.join(poses)}")
        print(f"Provider: {provider} ({model})")
        print(f"Output: {output_dir}")
        print()

    # Generate character sheet
    results = generate_character_sheet(
        description=args.description,
        poses=poses,
        style=args.style,
        provider=provider,
        model=model,
        output_dir=output_dir,
        reference_path=reference_path,
        parallel=args.parallel,
        quiet=args.json
    )

    # Save metadata
    meta_file = output_dir / "character_meta.json"
    with open(meta_file, "w") as f:
        json.dump({
            "description": args.description,
            "style": args.style,
            "poses": poses,
            "provider": provider,
            "model": model,
            "reference": str(reference_path) if reference_path else None,
            "files": [f["file"] for f in results["files"]]
        }, f, indent=2)

    results["metadata_file"] = str(meta_file)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print()
        if results["success"]:
            print_result(
                True,
                f"Generated {len(results['files'])}/{len(poses)} character poses",
                metadata={
                    "output_dir": str(output_dir),
                    "metadata": str(meta_file)
                }
            )
        else:
            print_result(False, "Character sheet generation failed")
            if results["errors"]:
                for err in results["errors"]:
                    print(f"  - {err['pose']}: {err['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
