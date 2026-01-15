#!/usr/bin/env python3
"""
Shared utilities for imagegen plugin.
"""

import base64
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

def generate_filename(prompt: str, prefix: str = "img", extension: str = "png",
                      include_timestamp: bool = True, include_hash: bool = True) -> str:
    """Generate a unique filename based on prompt and settings."""
    parts = [prefix]

    if include_timestamp:
        parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

    if include_hash:
        # Create a short hash from the prompt (SHA256 for better practice)
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        parts.append(prompt_hash)

    return "_".join(parts) + f".{extension}"

def sanitize_prompt(prompt: str) -> str:
    """Sanitize prompt for use in filenames."""
    # Remove special characters, keep alphanumeric and spaces
    sanitized = re.sub(r'[^\w\s-]', '', prompt)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Truncate to reasonable length
    return sanitized[:50]

def save_base64_image(b64_data: str, filepath: Path) -> Path:
    """Save base64-encoded image data to file."""
    # Remove data URI prefix if present
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]

    image_data = base64.b64decode(b64_data)
    with open(filepath, "wb") as f:
        f.write(image_data)
    return filepath

def load_image_as_base64(filepath: Path) -> str:
    """Load an image file and return as base64 string."""
    with open(filepath, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")

def get_image_mime_type(filepath: Path) -> str:
    """Get MIME type based on file extension."""
    ext = filepath.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif"
    }
    return mime_types.get(ext, "image/png")

def format_size_for_openai(size: str) -> str:
    """Convert size specification to OpenAI format."""
    size = size.lower().strip()

    # Handle common formats
    if size in ["1024x1024", "1536x1024", "1024x1536"]:
        return size
    if size == "square" or size == "1:1":
        return "1024x1024"
    if size == "landscape" or size == "16:9":
        return "1536x1024"
    if size == "portrait" or size == "9:16":
        return "1024x1536"
    if size == "auto":
        return "auto"

    return "1024x1024"  # default

def format_aspect_ratio_for_google(aspect_ratio: str) -> str:
    """Convert aspect ratio specification to Google format."""
    aspect_ratio = aspect_ratio.lower().strip()

    valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]

    if aspect_ratio in valid_ratios:
        return aspect_ratio
    if aspect_ratio == "square":
        return "1:1"
    if aspect_ratio == "landscape":
        return "16:9"
    if aspect_ratio == "portrait":
        return "9:16"
    if aspect_ratio == "wide":
        return "21:9"

    return "1:1"  # default

def print_result(success: bool, message: str, filepath: Optional[Path] = None,
                 metadata: Optional[dict] = None) -> None:
    """Print result in a structured format for the agent to parse."""
    status = "SUCCESS" if success else "ERROR"
    print(f"\n[{status}] {message}")

    if filepath:
        print(f"File: {filepath}")
        print(f"Absolute path: {filepath.resolve()}")

    if metadata:
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

def validate_api_key(provider: str) -> Tuple[bool, str]:
    """Check if API key is available for the provider."""
    if provider == "google":
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        env_var = "GEMINI_API_KEY or GOOGLE_API_KEY"
    elif provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        env_var = "OPENAI_API_KEY"
    else:
        return False, f"Unknown provider: {provider}"

    if not key:
        return False, f"API key not found. Set {env_var} environment variable."
    return True, "API key found"

def parse_provider_model(provider_model: str) -> Tuple[str, Optional[str]]:
    """
    Parse provider:model string.
    Examples:
        "google" -> ("google", None)
        "openai:gpt-image-1.5" -> ("openai", "gpt-image-1.5")
        "google:gemini-3-pro" -> ("google", "gemini-3-pro")
    """
    if ":" in provider_model:
        parts = provider_model.split(":", 1)
        return parts[0].lower(), parts[1]
    return provider_model.lower(), None

def estimate_cost(provider: str, model: str, num_images: int = 1) -> str:
    """Estimate cost for image generation (approximate)."""
    # These are rough estimates - actual pricing may vary
    costs = {
        "google": {
            "gemini-2.5-flash-image": 0.02,
            "gemini-3-pro-image-preview": 0.05
        },
        "openai": {
            "gpt-image-1-mini": 0.02,
            "gpt-image-1": 0.04,
            "gpt-image-1.5": 0.08
        }
    }

    if provider in costs and model in costs[provider]:
        cost_per_image = costs[provider][model]
        total = cost_per_image * num_images
        return f"~${total:.2f} ({num_images} image(s) @ ${cost_per_image:.2f} each)"
    return "Unknown"

if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")
    print(f"Generated filename: {generate_filename('A cute cat sitting on a couch')}")
    print(f"Sanitized prompt: {sanitize_prompt('A cute cat! @sitting on a couch??')}")
    print(f"Size formatting: {format_size_for_openai('landscape')}")
    print(f"Aspect ratio: {format_aspect_ratio_for_google('wide')}")
