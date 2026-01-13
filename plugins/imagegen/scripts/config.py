#!/usr/bin/env python3
"""
Configuration management for imagegen plugin.
Handles API keys, default settings, and output directories.
"""

import copy
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "default_provider": "google",  # "google" or "openai"
    "output_dir": "./generated-images",
    "google": {
        "model": "gemini-2.5-flash-image",  # or "gemini-3-pro-image-preview"
        "aspect_ratio": "1:1",
        "response_modalities": ["IMAGE"]
    },
    "openai": {
        "model": "gpt-image-1",  # or "gpt-image-1.5", "gpt-image-1-mini"
        "size": "1024x1024",
        "quality": "high",
        "background": "auto"
    },
    "naming": {
        "prefix": "img",
        "include_timestamp": True,
        "include_prompt_hash": True
    }
}

def get_config_path() -> Path:
    """Get the path to the config file."""
    # Store config in user's home directory
    config_dir = Path.home() / ".config" / "claude-imagegen"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from file, merging with defaults."""
    config_path = get_config_path()
    config = copy.deepcopy(DEFAULT_CONFIG)

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                # Deep merge
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config:
                        config[key] = {**config[key], **value}
                    else:
                        config[key] = value
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config: {e}")

    return config

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {config_path}")

def get_api_key(provider: str) -> Optional[str]:
    """Get API key for the specified provider from environment."""
    if provider == "google":
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    elif provider == "openai":
        return os.environ.get("OPENAI_API_KEY")
    return None

def set_config_value(key: str, value: Any) -> None:
    """Set a specific configuration value."""
    config = load_config()

    # Handle nested keys like "google.model"
    keys = key.split(".")
    target = config
    for k in keys[:-1]:
        if k not in target:
            target[k] = {}
        target = target[k]
    target[keys[-1]] = value

    save_config(config)
    print(f"Set {key} = {value}")

def get_config_value(key: str) -> Any:
    """Get a specific configuration value."""
    config = load_config()

    # Handle nested keys
    keys = key.split(".")
    target = config
    for k in keys:
        if isinstance(target, dict) and k in target:
            target = target[k]
        else:
            return None
    return target

def print_config() -> None:
    """Print current configuration."""
    config = load_config()
    print(json.dumps(config, indent=2))

def get_output_dir() -> Path:
    """Get the output directory, creating it if necessary."""
    config = load_config()
    output_dir = Path(config.get("output_dir", "./generated-images"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print_config()
    elif sys.argv[1] == "get" and len(sys.argv) >= 3:
        value = get_config_value(sys.argv[2])
        print(value if value is not None else f"Key '{sys.argv[2]}' not found")
    elif sys.argv[1] == "set" and len(sys.argv) >= 4:
        # Try to parse value as JSON, fall back to string
        try:
            value = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            value = sys.argv[3]
        set_config_value(sys.argv[2], value)
    elif sys.argv[1] == "path":
        print(get_config_path())
    else:
        print("Usage: config.py [get <key> | set <key> <value> | path]")
