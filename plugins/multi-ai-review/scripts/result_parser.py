#!/usr/bin/env python3
"""
Parse raw CLI output into structured findings.

Each CLI outputs differently, so we need specific parsers.
"""

import json
import re
import sys
import uuid
from pathlib import Path


def generate_finding_id() -> str:
    """Generate unique finding ID using full UUID to prevent collisions."""
    return str(uuid.uuid4())


def parse_severity(text: str) -> str:
    """Extract severity from text using word boundary matching."""
    text_lower = text.lower()
    # Use word boundaries to prevent substring matches (e.g., "flow" matching "low")
    if re.search(r'\b(critical|high|severe|urgent)\b', text_lower):
        return "critical"
    elif re.search(r'\b(major|important|significant)\b', text_lower):
        return "major"
    elif re.search(r'\b(minor|low|small)\b', text_lower):
        return "minor"
    return "trivial"


def parse_category(text: str) -> str:
    """Extract category from text using word boundary matching."""
    text_lower = text.lower()
    # Use word boundaries to prevent substring matches
    if re.search(r'\b(security|vulnerability|injection|xss|auth|csrf|owasp)\b', text_lower):
        return "security"
    elif re.search(r'\b(performance|slow|optimize|memory|cpu|n\+1|cache)\b', text_lower):
        return "performance"
    elif re.search(r'\b(architecture|design|pattern|structure|coupling|cohesion)\b', text_lower):
        return "architecture"
    elif re.search(r'\b(quality|readable|maintainable|clean|dry|duplicate)\b', text_lower):
        return "quality"
    return "best-practices"


def extract_file_line(text: str) -> tuple:
    """Extract file path and line number from text.

    Handles both Unix and Windows-style paths.
    """
    # Patterns for Unix and Windows paths
    patterns = [
        # Unix: path/to/file.ts:42
        r'([a-zA-Z0-9_\-./]+\.[a-zA-Z]+):(\d+)',
        # Windows: C:\path\to\file.ts:42 or path\to\file.ts:42
        r'([a-zA-Z]?:?[\\a-zA-Z0-9_\-./]+\.[a-zA-Z]+):(\d+)',
        # path/to/file.ts line 42
        r'([a-zA-Z0-9_\-./\\]+\.[a-zA-Z]+)\s+line\s+(\d+)',
        # Markdown-style: `path/to/file.ts:42`
        r'`([a-zA-Z0-9_\-./\\]+\.[a-zA-Z]+):(\d+)`',
        # **File**: `path/to/file.ts:42`
        r'\*\*File\*\*:\s*`?([a-zA-Z0-9_\-./\\]+\.[a-zA-Z]+):?(\d+)?`?',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            line_num = match.group(2) if match.lastindex >= 2 and match.group(2) else None
            return match.group(1), int(line_num) if line_num else None

    # Try to find just a file path (Unix or Windows)
    file_pattern = r'([a-zA-Z]?:?[\\a-zA-Z0-9_\-./]+\.[a-zA-Z]{1,4})'
    match = re.search(file_pattern, text)
    if match:
        return match.group(1), None

    return None, None


def _safe_get(item: dict, key: str, default: str = "") -> str:
    """Safely get a value from a dict, returning default if not a dict or key missing."""
    if not isinstance(item, dict):
        return default
    return item.get(key, default)


def parse_claude_output(raw_output: str) -> list[dict]:
    """Parse Claude Code CLI output."""
    findings = []

    # Claude typically outputs structured JSON or markdown
    # Try JSON first
    try:
        data = json.loads(raw_output)
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                desc = _safe_get(item, "description", "")
                findings.append({
                    "id": generate_finding_id(),
                    "source": "claude",
                    "category": _safe_get(item, "category") or parse_category(desc),
                    "severity": _safe_get(item, "severity") or parse_severity(desc),
                    "file": _safe_get(item, "file"),
                    "line": item.get("line"),
                    "description": desc,
                    "suggestion": _safe_get(item, "suggestion") or _safe_get(item, "fix")
                })
            return findings
        elif isinstance(data, dict) and "findings" in data:
            for item in data["findings"]:
                if not isinstance(item, dict):
                    continue
                desc = _safe_get(item, "description", "")
                findings.append({
                    "id": generate_finding_id(),
                    "source": "claude",
                    "category": _safe_get(item, "category") or parse_category(desc),
                    "severity": _safe_get(item, "severity") or parse_severity(desc),
                    "file": _safe_get(item, "file"),
                    "line": item.get("line"),
                    "description": desc,
                    "suggestion": _safe_get(item, "suggestion") or _safe_get(item, "fix")
                })
            return findings
    except json.JSONDecodeError:
        pass

    # Parse markdown/text format
    # Split by headers or numbered lists
    sections = re.split(r'\n(?=##\s+|\d+\.\s+|\*\s+\*\*)', raw_output)
    for section in sections:
        if not section.strip() or len(section.strip()) < 20:
            continue

        file_path, line = extract_file_line(section)

        findings.append({
            "id": generate_finding_id(),
            "source": "claude",
            "category": parse_category(section),
            "severity": parse_severity(section),
            "file": file_path,
            "line": line,
            "description": section[:500].strip(),
            "suggestion": ""
        })

    return findings


def parse_gemini_output(raw_output: str) -> list[dict]:
    """Parse Gemini CLI output."""
    findings = []

    # Try JSON first
    try:
        data = json.loads(raw_output)
        if isinstance(data, dict) and "findings" in data:
            for item in data["findings"]:
                if not isinstance(item, dict):
                    continue
                msg = _safe_get(item, "message", "")
                findings.append({
                    "id": generate_finding_id(),
                    "source": "gemini",
                    "category": _safe_get(item, "type") or parse_category(msg),
                    "severity": _safe_get(item, "severity") or parse_severity(msg),
                    "file": _safe_get(item, "path"),
                    "line": item.get("line"),
                    "description": msg,
                    "suggestion": _safe_get(item, "suggestion")
                })
            return findings
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                item_str = str(item)
                desc = _safe_get(item, "description", item_str[:500])
                findings.append({
                    "id": generate_finding_id(),
                    "source": "gemini",
                    "category": _safe_get(item, "category") or parse_category(item_str),
                    "severity": _safe_get(item, "severity") or parse_severity(item_str),
                    "file": _safe_get(item, "file"),
                    "line": item.get("line"),
                    "description": desc,
                    "suggestion": _safe_get(item, "suggestion")
                })
            return findings
    except json.JSONDecodeError:
        pass

    # Parse text format
    lines = raw_output.split("\n")
    current_finding = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r'^[\*\-]\s+', line) or re.match(r'^\d+\.\s+', line):
            if current_finding and len(current_finding["description"]) > 20:
                findings.append(current_finding)

            file_path, line_num = extract_file_line(line)
            current_finding = {
                "id": generate_finding_id(),
                "source": "gemini",
                "category": parse_category(line),
                "severity": parse_severity(line),
                "file": file_path,
                "line": line_num,
                "description": re.sub(r'^[\*\-\d.]+\s*', '', line),
                "suggestion": ""
            }
        elif current_finding:
            current_finding["description"] += " " + line

    if current_finding and len(current_finding["description"]) > 20:
        findings.append(current_finding)

    return findings


def parse_codex_output(raw_output: str) -> list[dict]:
    """Parse Codex CLI output."""
    findings = []

    # Try JSON first
    try:
        data = json.loads(raw_output)
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                item_str = str(item)
                findings.append({
                    "id": generate_finding_id(),
                    "source": "codex",
                    "category": _safe_get(item, "category") or parse_category(item_str),
                    "severity": _safe_get(item, "severity") or parse_severity(item_str),
                    "file": _safe_get(item, "file"),
                    "line": item.get("line"),
                    "description": _safe_get(item, "issue") or _safe_get(item, "description"),
                    "suggestion": _safe_get(item, "fix")
                })
            return findings
        elif isinstance(data, dict):
            if "issues" in data:
                for item in data["issues"]:
                    if not isinstance(item, dict):
                        continue
                    item_str = str(item)
                    findings.append({
                        "id": generate_finding_id(),
                        "source": "codex",
                        "category": _safe_get(item, "category") or parse_category(item_str),
                        "severity": _safe_get(item, "severity") or parse_severity(item_str),
                        "file": _safe_get(item, "file"),
                        "line": item.get("line"),
                        "description": _safe_get(item, "description"),
                        "suggestion": _safe_get(item, "fix")
                    })
                return findings
    except json.JSONDecodeError:
        pass

    # Parse text format (similar to Gemini parser)
    sections = re.split(r'\n(?=[\*\-\d])', raw_output)
    for section in sections:
        section = section.strip()
        if not section or len(section) < 20:
            continue

        file_path, line = extract_file_line(section)

        findings.append({
            "id": generate_finding_id(),
            "source": "codex",
            "category": parse_category(section),
            "severity": parse_severity(section),
            "file": file_path,
            "line": line,
            "description": section[:500],
            "suggestion": ""
        })

    return findings


def parse_cli_output(cli: str, output_file: Path) -> list[dict]:
    """Parse output from a CLI's output file."""
    if not output_file.exists():
        return []

    try:
        with open(output_file) as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse {output_file}: {e}", file=sys.stderr)
        return []

    raw_output = data.get("stdout", "")

    parsers = {
        "claude": parse_claude_output,
        "gemini": parse_gemini_output,
        "codex": parse_codex_output
    }

    parser = parsers.get(cli)
    if parser:
        return parser(raw_output)

    return []


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: result_parser.py <cli> <output_file>", file=sys.stderr)
        sys.exit(1)

    cli = sys.argv[1]
    output_file = Path(sys.argv[2])
    findings = parse_cli_output(cli, output_file)
    print(json.dumps(findings, indent=2))
