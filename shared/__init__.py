"""
Shared utilities for claude-code-plugins.

This package provides common functionality used across multiple plugins:
- security: SSRF protection, path validation, shell/AppleScript escaping
- config: YAML/JSON loading, API key management, output directories
- output: Result formatting, JSON output, error handling
- cli_configs: Unified CLI configurations for Claude/Gemini/Codex
"""

from .security import (
    is_safe_url,
    safe_path,
    match_path_pattern,
    escape_for_shell,
    escape_for_applescript,
    validate_command_whitelist,
)

from .config import (
    load_yaml_config,
    load_json_config,
    get_api_key,
    get_output_dir,
)

from .output import (
    print_result,
    json_output,
    error_exit,
)

from .cli_configs import (
    CLI_CONFIGS,
    get_model,
    build_command,
)

__all__ = [
    # security
    "is_safe_url",
    "safe_path",
    "match_path_pattern",
    "escape_for_shell",
    "escape_for_applescript",
    "validate_command_whitelist",
    # config
    "load_yaml_config",
    "load_json_config",
    "get_api_key",
    "get_output_dir",
    # output
    "print_result",
    "json_output",
    "error_exit",
    # cli_configs
    "CLI_CONFIGS",
    "get_model",
    "build_command",
]
