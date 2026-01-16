#!/usr/bin/env python3
"""
Unified CLI configurations for AI assistants.

Provides configurations for Claude, Gemini, and Codex CLIs,
used by both fork-terminal and multi-ai-review plugins.
"""

import os
import shlex
from typing import List, Optional


# Unified CLI configurations
CLI_CONFIGS = {
    "claude": {
        "command": "claude",
        "default_model": "opus",
        "fast_model": "sonnet",
        "env_model": "MULTI_REVIEW_CLAUDE_MODEL",
        # Flags for different modes
        "model_flag": "--model",
        "prompt_flag": "-p",  # For autonomous mode (run and exit)
        "auto_flags": ["--dangerously-skip-permissions"],
        # Command templates for different use cases
        "interactive_template": "{command} --model {model} --dangerously-skip-permissions '{prompt}'",
        "autonomous_template": "{command} --model {model} --dangerously-skip-permissions -p '{prompt}'",
        "review_template": "{command} --model {model} --dangerously-skip-permissions -p '{prompt}'",
        # Installation
        "install_cmd": "Already available (Claude Code CLI)",
        "check_cmd": "which claude",
    },
    "gemini": {
        "command": "gemini",
        "default_model": "gemini-3-pro-preview",
        "fast_model": "gemini-3-flash-preview",
        "env_model": "MULTI_REVIEW_GEMINI_MODEL",
        "model_flag": "--model",
        "prompt_flag": None,  # Gemini takes prompt positionally after --
        "auto_flags": ["-y"],
        "interactive_template": "{command} --model {model} -y -i '{prompt}'",
        "autonomous_template": "{command} --model {model} -y '{prompt}'",
        "review_template": "{command} --model {model} -y '{prompt}'",
        "install_cmd": "npm install -g @google/gemini-cli",
        "check_cmd": "which gemini",
    },
    "codex": {
        "command": "codex",
        "default_model": "gpt-5.2-codex",
        "fast_model": "gpt-5.1-codex-mini",
        "env_model": "MULTI_REVIEW_CODEX_MODEL",
        "model_flag": "--model",
        "prompt_flag": None,  # Codex takes prompt positionally
        "auto_flags": ["--full-auto"],
        "interactive_template": "{command} --model {model} --dangerously-bypass-approvals-and-sandbox '{prompt}'",
        "autonomous_template": "{command} --model {model} --dangerously-bypass-approvals-and-sandbox '{prompt}'",
        "review_template": "{command} --model {model} --full-auto '{prompt}'",
        "install_cmd": "npm install -g @openai/codex",
        "check_cmd": "which codex",
    }
}


def get_model(cli: str, fast: bool = False) -> str:
    """Get model for CLI from environment or defaults.

    Args:
        cli: CLI name ("claude", "gemini", "codex").
        fast: If True, use the fast model instead of default.

    Returns:
        Model name to use.

    Raises:
        ValueError: If CLI is unknown.
    """
    config = CLI_CONFIGS.get(cli)
    if not config:
        raise ValueError(f"Unknown CLI: {cli}. Supported: {list(CLI_CONFIGS.keys())}")

    # Check environment variable first
    env_model = os.environ.get(config["env_model"])
    if env_model:
        return env_model

    return config["fast_model"] if fast else config["default_model"]


def build_command(
    cli: str,
    prompt: str,
    model: Optional[str] = None,
    mode: str = "review"
) -> str:
    """Build command string for a CLI.

    Args:
        cli: CLI name ("claude", "gemini", "codex").
        prompt: Prompt to pass to the CLI.
        model: Model to use (default: from config/env).
        mode: Command mode - "interactive", "autonomous", or "review".

    Returns:
        Complete command string.

    Raises:
        ValueError: If CLI or mode is unknown.
    """
    config = CLI_CONFIGS.get(cli)
    if not config:
        raise ValueError(f"Unknown CLI: {cli}. Supported: {list(CLI_CONFIGS.keys())}")

    template_key = f"{mode}_template"
    if template_key not in config:
        raise ValueError(f"Unknown mode: {mode}. Supported: interactive, autonomous, review")

    model = model or get_model(cli)

    # Escape prompt for shell single-quoted strings
    safe_prompt = prompt.replace("'", "'\\''")

    # Validate model name - only allow alphanumeric, dash, underscore, and dot
    # This prevents shell injection without needing to strip quotes
    import re
    if not re.match(r'^[\w\-\.]+$', model):
        raise ValueError(f"Invalid model name: {model}. Only alphanumeric, dash, underscore, and dot allowed.")
    safe_model = model

    # Build command from template
    cmd = config[template_key].format(
        command=config["command"],
        model=safe_model,
        prompt=safe_prompt
    )

    # Clean up any double spaces from empty template fields
    return " ".join(cmd.split())


def build_command_list(
    cli: str,
    prompt: str,
    model: Optional[str] = None
) -> List[str]:
    """Build command as a list (for subprocess).

    Args:
        cli: CLI name.
        prompt: Prompt to pass.
        model: Model to use.

    Returns:
        Command as list of strings.
    """
    config = CLI_CONFIGS.get(cli)
    if not config:
        raise ValueError(f"Unknown CLI: {cli}")

    model = model or get_model(cli)
    cmd = [config["command"]]

    # Add model
    if config["model_flag"]:
        cmd.extend([config["model_flag"], model])

    # Add auto flags
    cmd.extend(config["auto_flags"])

    # Add prompt
    if config["prompt_flag"]:
        cmd.extend([config["prompt_flag"], prompt])
    else:
        cmd.append(prompt)

    return cmd


def get_install_instructions() -> str:
    """Get installation instructions for all CLIs.

    Returns:
        Markdown-formatted installation instructions.
    """
    lines = ["# CLI Installation Instructions\n"]

    for cli, config in CLI_CONFIGS.items():
        lines.append(f"## {cli.title()}")
        lines.append("```bash")
        lines.append(config["install_cmd"])
        lines.append("```\n")

    return "\n".join(lines)


def is_cli_available(cli: str) -> bool:
    """Check if a CLI is installed and available.

    Args:
        cli: CLI name.

    Returns:
        True if CLI is available.
    """
    import subprocess

    config = CLI_CONFIGS.get(cli)
    if not config:
        return False

    result = subprocess.run(
        config["check_cmd"].split(),
        capture_output=True
    )
    return result.returncode == 0


def get_available_clis() -> List[str]:
    """Get list of available CLIs.

    Returns:
        List of CLI names that are installed.
    """
    return [cli for cli in CLI_CONFIGS if is_cli_available(cli)]


if __name__ == "__main__":
    # Run basic tests
    print("Testing CLI configs...")

    # Test get_model
    model = get_model("claude")
    assert model == "opus", f"Expected opus, got {model}"
    print(f"  Default Claude model: {model}")

    fast_model = get_model("gemini", fast=True)
    assert fast_model == "gemini-3-flash-preview"
    print(f"  Fast Gemini model: {fast_model}")

    # Test build_command
    cmd = build_command("claude", "Review this code", mode="review")
    print(f"  Claude review command: {cmd}")
    assert "--dangerously-skip-permissions" in cmd

    cmd = build_command("gemini", "Help me debug", mode="interactive")
    print(f"  Gemini interactive command: {cmd}")
    assert "-y -i" in cmd

    # Test command list
    cmd_list = build_command_list("codex", "Test prompt")
    print(f"  Codex command list: {cmd_list}")
    assert cmd_list[0] == "codex"

    # Test installation instructions
    instructions = get_install_instructions()
    assert "Claude" in instructions
    assert "Gemini" in instructions
    assert "Codex" in instructions
    print("  Installation instructions: Generated")

    # Check available CLIs
    available = get_available_clis()
    print(f"  Available CLIs: {available}")

    print("\nAll tests passed!")
