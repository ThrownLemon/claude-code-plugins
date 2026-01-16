#!/usr/bin/env python3
"""
Output utilities for claude-code-plugins.

Provides consistent result formatting, JSON output, and error handling
for all plugin scripts.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def print_result(
    success: bool,
    message: str,
    filepath: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Print result in a structured format for the agent to parse.

    Args:
        success: Whether the operation succeeded.
        message: Status message.
        filepath: Optional path to output file.
        metadata: Optional dictionary of additional metadata.

    Examples:
        >>> print_result(True, "Image generated successfully", Path("/tmp/image.png"))
        [SUCCESS] Image generated successfully
        File: /tmp/image.png
        Absolute path: /tmp/image.png
    """
    status = "SUCCESS" if success else "ERROR"
    print(f"\n[{status}] {message}")

    if filepath:
        print(f"File: {filepath}")
        print(f"Absolute path: {filepath.resolve()}")

    if metadata:
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")


def json_output(
    data: Dict[str, Any],
    indent: int = 2,
    file: Any = None
) -> None:
    """Print data as formatted JSON.

    Args:
        data: Dictionary to output as JSON.
        indent: Indentation level (default: 2).
        file: Output file object (default: stdout).
    """
    print(json.dumps(data, indent=indent, default=str), file=file or sys.stdout)


def error_exit(message: str, code: int = 1) -> None:
    """Print error message and exit with code.

    Args:
        message: Error message to print.
        code: Exit code (default: 1).
    """
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def success_result(
    message: str,
    filepath: Optional[Path] = None,
    **metadata: Any
) -> Dict[str, Any]:
    """Create a success result dictionary.

    Args:
        message: Success message.
        filepath: Optional output file path.
        **metadata: Additional metadata fields.

    Returns:
        Dictionary with success=True and all provided fields.
    """
    result = {
        "success": True,
        "message": message,
        **metadata
    }
    if filepath:
        result["file"] = str(filepath)
        result["absolute_path"] = str(filepath.resolve())
    return result


def error_result(
    error: str,
    **metadata: Any
) -> Dict[str, Any]:
    """Create an error result dictionary.

    Args:
        error: Error message.
        **metadata: Additional metadata fields.

    Returns:
        Dictionary with success=False and error message.
    """
    return {
        "success": False,
        "error": error,
        **metadata
    }


def format_table(
    headers: list,
    rows: list,
    column_widths: Optional[list] = None
) -> str:
    """Format data as an ASCII table.

    Args:
        headers: List of column headers.
        rows: List of row data (list of lists).
        column_widths: Optional list of column widths.

    Returns:
        Formatted table string.
    """
    if not column_widths:
        # Auto-calculate widths
        column_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            column_widths.append(max_width)

    # Format header
    header_parts = []
    for i, (header, width) in enumerate(zip(headers, column_widths)):
        header_parts.append(str(header).ljust(width))
    header_line = " ".join(header_parts)

    # Format separator
    separator = "-" * len(header_line)

    # Format rows
    row_lines = []
    for row in rows:
        row_parts = []
        for i, width in enumerate(column_widths):
            value = str(row[i]) if i < len(row) else ""
            # Truncate if necessary, ensuring width > 3 for ellipsis
            if len(value) > width:
                if width > 3:
                    value = value[:width-3] + "..."
                else:
                    # For very narrow columns, just truncate without ellipsis
                    value = value[:width]
            row_parts.append(value.ljust(width))
        row_lines.append(" ".join(row_parts))

    return "\n".join([header_line, separator] + row_lines)


if __name__ == "__main__":
    # Run basic tests
    print("Testing output utilities...")

    # Test print_result
    print("\nTest print_result:")
    print_result(True, "Test succeeded", Path("/tmp/test.txt"), {"key": "value"})

    # Test JSON output
    print("\nTest json_output:")
    json_output({"test": True, "value": 42})

    # Test result helpers
    print("\nTest success_result:")
    result = success_result("Operation complete", Path("/tmp/out.png"), provider="google")
    print(result)

    print("\nTest error_result:")
    result = error_result("Something went wrong", provider="openai")
    print(result)

    # Test table formatting
    print("\nTest format_table:")
    headers = ["ID", "Name", "Status"]
    rows = [
        [1, "Task A", "Complete"],
        [2, "Task B", "Pending"],
        [3, "Very Long Task Name", "In Progress"],
    ]
    print(format_table(headers, rows))

    print("\nAll tests passed!")
