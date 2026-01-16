#!/usr/bin/env python3
"""
Security utilities for claude-code-plugins.

Provides SSRF protection, path validation, and various escaping functions
for safe command execution across different contexts.
"""

import fnmatch
import ipaddress
import os
import shlex
from typing import List, Optional
from urllib.parse import urlparse


def is_safe_url(url: str, resolve_dns: bool = True) -> bool:
    """Validate URL to prevent SSRF attacks including DNS rebinding.

    Rejects private IP ranges, localhost, cloud metadata endpoints,
    and optionally resolves hostnames to check their actual IP addresses.

    Args:
        url: URL to validate.
        resolve_dns: If True, resolve hostname and check resolved IP.
                     Helps prevent DNS rebinding attacks.

    Returns:
        True if URL is safe to fetch, False otherwise.

    Examples:
        >>> is_safe_url("https://example.com/image.png")
        True
        >>> is_safe_url("http://localhost:8080/secret")
        False
        >>> is_safe_url("http://169.254.169.254/metadata")
        False
    """
    import socket

    try:
        parsed = urlparse(url)
        host = parsed.hostname
        scheme = parsed.scheme

        if not host:
            return False

        # Only allow http and https schemes
        if scheme not in ('http', 'https'):
            return False

        # Check for localhost variants
        if host.lower() in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            return False

        # Check for cloud metadata endpoints
        metadata_hosts = (
            '169.254.169.254',
            'metadata.google.internal',
            'metadata.google.com',
            'metadata.aws.amazon.com',
            'instance-data',
            '100.100.100.200',  # Alibaba Cloud metadata
        )
        if host.lower() in metadata_hosts:
            return False

        # Try to parse as IP address and check for private ranges
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            # Not an IP address - it's a hostname
            # Resolve it to check the actual IP (prevents DNS rebinding)
            if resolve_dns:
                try:
                    resolved_ip = socket.gethostbyname(host)
                    ip = ipaddress.ip_address(resolved_ip)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                        return False
                except (socket.gaierror, ValueError):
                    # Can't resolve - be cautious but allow (might be valid external host)
                    # The actual request will fail anyway if it can't resolve
                    pass

        return True
    except Exception:
        return False


def safe_path(path: str) -> str:
    """Resolve path with symlink resolution for security.

    Prevents path traversal attacks via symlinks by resolving
    the actual path on the filesystem.

    Args:
        path: Path to resolve.

    Returns:
        Resolved absolute path with symlinks followed.

    Examples:
        >>> safe_path("/tmp/../etc/passwd")
        '/etc/passwd'
    """
    expanded = os.path.expanduser(path)
    return os.path.realpath(os.path.normpath(expanded))


def is_glob_pattern(pattern: str) -> bool:
    """Check if pattern contains glob wildcards.

    Args:
        pattern: Pattern to check.

    Returns:
        True if pattern contains *, ?, or [ characters.
    """
    return '*' in pattern or '?' in pattern or '[' in pattern


def match_path_pattern(file_path: str, pattern: str) -> bool:
    """Match file path against pattern with symlink resolution.

    Supports both prefix matching and glob patterns.
    Resolves symlinks to prevent bypass attacks.

    Args:
        file_path: File path to check.
        pattern: Pattern to match against (can be prefix or glob).

    Returns:
        True if path matches the pattern.

    Examples:
        >>> match_path_pattern("/etc/passwd", "/etc")
        True
        >>> match_path_pattern("/home/user/.env", "*.env")
        True
    """
    expanded_pattern = os.path.expanduser(pattern)
    # Resolve symlinks to prevent bypass via symlinked paths
    normalized = os.path.realpath(os.path.normpath(file_path))
    expanded_normalized = os.path.expanduser(normalized)

    if is_glob_pattern(pattern):
        basename = os.path.basename(expanded_normalized)
        basename_lower = basename.lower()
        pattern_lower = pattern.lower()
        expanded_pattern_lower = expanded_pattern.lower()

        if fnmatch.fnmatch(basename_lower, expanded_pattern_lower):
            return True
        if fnmatch.fnmatch(basename_lower, pattern_lower):
            return True
        if fnmatch.fnmatch(expanded_normalized.lower(), expanded_pattern_lower):
            return True
        return False
    else:
        # Prefix matching: ensure we match directory boundaries properly
        expanded_pattern_normalized = expanded_pattern.rstrip('/')
        if expanded_normalized == expanded_pattern_normalized:
            return True
        if expanded_normalized.startswith(expanded_pattern_normalized + '/'):
            return True
        return False


def escape_for_shell(text: str) -> str:
    """Escape text for safe use in shell commands.

    Uses shlex.quote for proper POSIX shell escaping.

    Args:
        text: Text to escape.

    Returns:
        Shell-escaped string.

    Examples:
        >>> escape_for_shell("hello world")
        "'hello world'"
        >>> escape_for_shell("it's a test")
        "'it'\"'\"'s a test'"
    """
    return shlex.quote(text)


def escape_for_applescript(text: str) -> str:
    """Escape text for safe use in AppleScript double-quoted strings.

    Escapes backslashes, double quotes, and control characters that
    could cause AppleScript injection vulnerabilities.

    Args:
        text: Text to escape.

    Returns:
        AppleScript-safe string.

    Examples:
        >>> escape_for_applescript('echo "hello"')
        'echo \\"hello\\"'
        >>> escape_for_applescript("line1\\nline2")
        'line1\\\\nline2'
    """
    return (text
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t"))


def escape_single_quotes(text: str) -> str:
    """Escape single quotes for shell single-quoted strings.

    The standard method: end the string, add an escaped quote, restart the string.

    Args:
        text: Text to escape.

    Returns:
        String with single quotes escaped.

    Examples:
        >>> escape_single_quotes("it's a test")
        "it'\\''s a test"
    """
    return text.replace("'", "'\\''")


def validate_command_whitelist(
    command: str,
    whitelist: List[str],
    default_whitelist: Optional[List[str]] = None
) -> bool:
    """Validate that a command is in the allowed whitelist.

    Checks only the command name (first word), not arguments.

    Args:
        command: Full command string.
        whitelist: List of allowed command names.
        default_whitelist: Optional default whitelist to use if whitelist is empty.

    Returns:
        True if command is allowed.

    Examples:
        >>> validate_command_whitelist("echo hello", ["echo", "date"])
        True
        >>> validate_command_whitelist("rm -rf /", ["echo", "date"])
        False
    """
    # Extract command name (first word)
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return False

    cmd_name = os.path.basename(cmd_parts[0])

    # Use default whitelist if provided and whitelist is empty
    effective_whitelist = whitelist if whitelist else (default_whitelist or [])

    return cmd_name in effective_whitelist


# Default whitelist for widget commands (conservative list of safe commands)
DEFAULT_WIDGET_WHITELIST = [
    "date", "uptime", "whoami", "hostname", "pwd",
    "echo", "basename", "dirname", "uname", "id",
]


if __name__ == "__main__":
    # Run basic tests
    print("Testing security utilities...")

    # SSRF tests
    assert is_safe_url("https://example.com/image.png") is True
    assert is_safe_url("http://localhost:8080/secret") is False
    assert is_safe_url("http://169.254.169.254/metadata") is False
    assert is_safe_url("http://192.168.1.1/admin") is False
    print("  SSRF checks: PASS")

    # Path tests - verify realpath is used (resolves symlinks)
    resolved = safe_path("/tmp/../etc/passwd")
    assert resolved.endswith("/etc/passwd"), f"Expected path ending in /etc/passwd, got {resolved}"
    print("  Path resolution: PASS")

    # Escaping tests
    assert escape_for_applescript('echo "hello"') == 'echo \\"hello\\"'
    assert escape_single_quotes("it's a test") == "it'\\''s a test"
    print("  Escaping: PASS")

    # Whitelist tests
    assert validate_command_whitelist("echo hello", ["echo", "date"]) is True
    assert validate_command_whitelist("rm -rf /", ["echo", "date"]) is False
    print("  Whitelist: PASS")

    print("\nAll tests passed!")
