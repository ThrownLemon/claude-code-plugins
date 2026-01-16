#!/usr/bin/env python3
"""
Configuration utilities for claude-code-plugins.

Provides unified configuration loading from YAML/JSON files,
API key management, and output directory handling.
"""

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Try to import yaml, but don't require it
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_yaml_config(
    path: Path,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML config file.
        defaults: Default values to use if file doesn't exist or keys are missing.

    Returns:
        Merged configuration dictionary.

    Raises:
        ImportError: If PyYAML is not installed.
        yaml.YAMLError: If the YAML file is malformed.
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is required for YAML config loading. Install with: pip install pyyaml")

    config = copy.deepcopy(defaults) if defaults else {}

    if not path.exists():
        return config

    with open(path, "r") as f:
        user_config = yaml.safe_load(f) or {}

    # Deep merge user config into defaults
    return _deep_merge(config, user_config)


def load_json_config(
    path: Path,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load configuration from a JSON file.

    Args:
        path: Path to the JSON config file.
        defaults: Default values to use if file doesn't exist or keys are missing.

    Returns:
        Merged configuration dictionary.
    """
    config = copy.deepcopy(defaults) if defaults else {}

    if not path.exists():
        return config

    try:
        with open(path, "r") as f:
            user_config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON config at {path}: {e}", file=sys.stderr)
        return config

    # Deep merge user config into defaults
    return _deep_merge(config, user_config)


def save_json_config(path: Path, config: Dict[str, Any]) -> None:
    """Save configuration to a JSON file.

    Args:
        path: Path to save the config file.
        config: Configuration dictionary to save.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        base: Base dictionary (defaults).
        override: Override dictionary (user values).

    Returns:
        Merged dictionary with override values taking precedence.
    """
    result = copy.deepcopy(base)

    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def get_nested_value(config: Dict[str, Any], key: str) -> Any:
    """Get a nested configuration value using dot notation.

    Args:
        config: Configuration dictionary.
        key: Dot-separated key path (e.g., "google.model").

    Returns:
        The value at the key path, or None if not found.

    Examples:
        >>> get_nested_value({"a": {"b": 1}}, "a.b")
        1
        >>> get_nested_value({"a": {"b": 1}}, "a.c")
        None
    """
    keys = key.split(".")
    target = config

    for k in keys:
        if isinstance(target, dict) and k in target:
            target = target[k]
        else:
            return None

    return target


def set_nested_value(config: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Set a nested configuration value using dot notation.

    Args:
        config: Configuration dictionary (modified in place).
        key: Dot-separated key path (e.g., "google.model").
        value: Value to set.

    Returns:
        The modified config dictionary.

    Raises:
        TypeError: If an intermediate key exists but is not a dictionary.
    """
    keys = key.split(".")
    target = config

    for k in keys[:-1]:
        if k not in target:
            target[k] = {}
        elif not isinstance(target[k], dict):
            raise TypeError(
                f"Cannot set nested key '{key}': intermediate key '{k}' "
                f"exists but is not a dictionary (type: {type(target[k]).__name__})"
            )
        target = target[k]

    target[keys[-1]] = value
    return config


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a provider from environment variables.

    Supports multiple environment variable names per provider.

    Args:
        provider: Provider name ("google", "openai", etc.).

    Returns:
        API key if found, None otherwise.
    """
    env_vars = {
        "google": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
    }

    for env_var in env_vars.get(provider, []):
        key = os.environ.get(env_var)
        if key:
            return key

    return None


def get_plugin_config_dir(plugin_name: str) -> Path:
    """Get the configuration directory for a plugin.

    Creates the directory if it doesn't exist.

    Args:
        plugin_name: Name of the plugin.

    Returns:
        Path to the plugin's config directory.

    Raises:
        ValueError: If plugin_name contains path traversal characters.
    """
    import re
    # Sanitize plugin_name to prevent path traversal attacks
    # Only allow alphanumeric, dash, and underscore
    if not re.match(r'^[\w\-]+$', plugin_name):
        raise ValueError(f"Invalid plugin name: {plugin_name}. Only alphanumeric, dash, and underscore allowed.")

    # Additional check: ensure no path separators after sanitization
    if '/' in plugin_name or '\\' in plugin_name or '..' in plugin_name:
        raise ValueError(f"Invalid plugin name: {plugin_name}. Path separators not allowed.")

    config_dir = Path.home() / ".config" / f"claude-{plugin_name}"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_output_dir(
    plugin_name: str,
    subdirectory: Optional[str] = None
) -> Path:
    """Get the output directory for a plugin.

    Creates the directory if it doesn't exist.

    Args:
        plugin_name: Name of the plugin.
        subdirectory: Optional subdirectory within the output dir.

    Returns:
        Path to the output directory.
    """
    # Check for environment variable override
    env_output = os.environ.get(f"CLAUDE_{plugin_name.upper()}_OUTPUT_DIR")
    if env_output:
        output_dir = Path(env_output)
    else:
        # Default to current directory with generated-* folder
        output_dir = Path.cwd() / f"generated-{plugin_name}"

    if subdirectory:
        output_dir = output_dir / subdirectory

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


if __name__ == "__main__":
    # Run basic tests
    print("Testing config utilities...")

    # Test deep merge
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"c": 5}, "e": 6}
    merged = _deep_merge(base, override)
    assert merged == {"a": 1, "b": {"c": 5, "d": 3}, "e": 6}
    print("  Deep merge: PASS")

    # Test nested value access
    config = {"google": {"model": "gemini-2.5-flash"}}
    assert get_nested_value(config, "google.model") == "gemini-2.5-flash"
    assert get_nested_value(config, "google.missing") is None
    print("  Nested value access: PASS")

    # Test nested value set
    set_nested_value(config, "google.size", "1024x1024")
    assert config["google"]["size"] == "1024x1024"
    print("  Nested value set: PASS")

    print("\nAll tests passed!")
