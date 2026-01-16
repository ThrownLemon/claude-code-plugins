#!/usr/bin/env python3
"""CLI configuration for each AI tool.

This module re-exports CLI configurations from the shared library.
For backwards compatibility, it maintains the same interface.
"""

import sys
from pathlib import Path

# Add shared directory to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import from shared (with fallback)
try:
    from shared.cli_configs import (
        CLI_CONFIGS,
        get_model,
        build_command_list as build_review_command,
        get_install_instructions,
    )
except ImportError:
    # Fallback if shared not available
    import os
    from typing import Optional

    CLI_CONFIGS = {
        "claude": {
            "command": "claude",
            "default_model": "opus",
            "fast_model": "sonnet",
            "env_model": "MULTI_REVIEW_CLAUDE_MODEL",
            "prompt_flag": "-p",
            "model_flag": "--model",
            "auto_flags": ["--dangerously-skip-permissions"],
            "install_cmd": "Already available (Claude Code CLI)",
            "check_cmd": "which claude"
        },
        "gemini": {
            "command": "gemini",
            "default_model": "gemini-3-pro-preview",
            "fast_model": "gemini-3-flash-preview",
            "env_model": "MULTI_REVIEW_GEMINI_MODEL",
            "prompt_flag": None,
            "model_flag": "--model",
            "auto_flags": ["-y"],
            "install_cmd": "npm install -g @google/gemini-cli",
            "check_cmd": "which gemini"
        },
        "codex": {
            "command": "codex",
            "default_model": "gpt-5.2-codex",
            "fast_model": "gpt-5.1-codex-mini",
            "env_model": "MULTI_REVIEW_CODEX_MODEL",
            "prompt_flag": None,
            "model_flag": "--model",
            "auto_flags": ["--full-auto"],
            "install_cmd": "npm install -g @openai/codex",
            "check_cmd": "which codex"
        }
    }

    def get_model(cli: str) -> str:
        """Get model for CLI from env or default."""
        config = CLI_CONFIGS.get(cli)
        if not config:
            raise ValueError(f"Unknown CLI: {cli}")
        return os.environ.get(config["env_model"], config["default_model"])

    def build_review_command(cli: str, prompt: str, model: Optional[str] = None) -> list[str]:
        """Build the command to run a review."""
        config = CLI_CONFIGS.get(cli)
        if not config:
            raise ValueError(f"Unknown CLI: {cli}")

        model = model or get_model(cli)
        cmd = [config["command"]]

        if config["model_flag"]:
            cmd.extend([config["model_flag"], model])

        cmd.extend(config["auto_flags"])

        if config["prompt_flag"]:
            cmd.extend([config["prompt_flag"], prompt])
        else:
            cmd.append(prompt)

        return cmd

    def get_install_instructions() -> str:
        """Get installation instructions for all CLIs."""
        lines = ["# CLI Installation Instructions\n"]
        for cli, config in CLI_CONFIGS.items():
            lines.append(f"## {cli.title()}")
            lines.append("```bash")
            lines.append(config["install_cmd"])
            lines.append("```\n")
        return "\n".join(lines)


# Re-export for backwards compatibility
__all__ = [
    "CLI_CONFIGS",
    "get_model",
    "build_review_command",
    "get_install_instructions",
]
