#!/usr/bin/env python3
"""
Format aggregated findings into readable reports.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from aggregator import aggregate_findings


def severity_emoji(severity: str) -> str:
    """Get emoji for severity level."""
    return {
        "critical": "[CRITICAL]",
        "major": "[MAJOR]",
        "minor": "[MINOR]",
        "trivial": "[TRIVIAL]"
    }.get(severity, "[?]")


def _safe_str(value) -> str:
    """Safely convert a value to string, handling None and non-string types."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def format_finding(finding: dict, index: int) -> list[str]:
    """Format a single consensus/majority finding."""
    category = _safe_str(finding.get("category", "Unknown")).replace("-", " ").title()
    lines = [
        f"### {index}. {category} Issue",
        ""
    ]

    if finding.get("file"):
        file_line = _safe_str(finding["file"])
        if finding.get("line"):
            file_line += f":{finding['line']}"
        lines.append(f"**File**: `{file_line}`")

    severity = _safe_str(finding.get("severity", "unknown")).title()
    lines.append(f"**Severity**: {severity_emoji(finding.get('severity'))} {severity}")
    lines.append(f"**Agreement**: {', '.join(finding.get('sources', []))}")
    lines.append("")

    # Show each CLI's description
    descriptions = finding.get("descriptions")
    if descriptions and isinstance(descriptions, dict):
        lines.append("**Reviewer Notes**:")
        for cli, desc in descriptions.items():
            desc_str = _safe_str(desc)
            truncated = desc_str[:300] + "..." if len(desc_str) > 300 else desc_str
            # Clean up the description
            truncated = truncated.replace("\n", " ").strip()
            lines.append(f"- **{cli}**: {truncated}")
        lines.append("")

    # Show suggestions if any
    suggestions = finding.get("suggestions")
    if suggestions and isinstance(suggestions, dict):
        non_empty_suggestions = {k: v for k, v in suggestions.items() if v}
        if non_empty_suggestions:
            lines.append("**Suggested Fixes**:")
            for cli, suggestion in non_empty_suggestions.items():
                sugg_str = _safe_str(suggestion)
                truncated = sugg_str[:200] + "..." if len(sugg_str) > 200 else sugg_str
                lines.append(f"- **{cli}**: {truncated}")
            lines.append("")

    lines.extend(["---", ""])
    return lines


def format_unique_finding(finding: dict, index: int) -> list[str]:
    """Format a unique finding (shorter format)."""
    lines = []

    file_info = _safe_str(finding.get("file", "Unknown file"))
    if finding.get("line"):
        file_info += f":{finding['line']}"

    severity = severity_emoji(finding.get("severity"))
    desc = _safe_str(finding.get("description", ""))[:100].replace("\n", " ")

    lines.append(f"{index}. {severity} `{file_info}` - {desc}")

    return lines


def format_markdown_report(data: dict) -> str:
    """Generate a markdown comparison report."""
    # Use UTC timestamp for consistency
    timestamp = data["metadata"].get("started", datetime.now(timezone.utc).isoformat())

    lines = [
        "# Multi-AI Code Review Report",
        "",
        f"**Review ID**: `{data['review_id']}`",
        f"**Project**: `{data['metadata'].get('project_root', 'Unknown')}`",
        f"**Date**: {timestamp}",
        f"**CLIs**: {', '.join(data['metadata'].get('available_clis', []))}",
        "",
    ]

    # Show missing CLIs warning if any
    missing = data["metadata"].get("missing_clis", [])
    if missing:
        lines.append(f"**Warning**: Missing CLIs: {', '.join(missing)}")
        lines.append("")

    lines.extend(["---", "", "## Summary", ""])

    # Summary table
    lines.append("| Agreement Level | Count | Description |")
    lines.append("|-----------------|-------|-------------|")
    lines.append(f"| Consensus | {len(data['consensus'])} | All CLIs agree |")
    lines.append(f"| Majority | {len(data['majority'])} | 2+ CLIs agree |")

    # Add unique counts
    total_unique = sum(len(v) for v in data["unique"].values())
    lines.append(f"| Unique | {total_unique} | Only one CLI found |")
    lines.append(f"| **Total** | **{data['total_findings']}** | All findings |")
    lines.extend(["", "---", ""])

    # Category breakdown
    if data.get("by_severity"):
        lines.extend(["### By Severity", ""])
        for severity in ["critical", "major", "minor", "trivial"]:
            count = len(data["by_severity"].get(severity, []))
            if count > 0:
                lines.append(f"- {severity_emoji(severity)} **{severity.title()}**: {count}")
        lines.extend(["", "---", ""])

    # Consensus findings
    if data["consensus"]:
        lines.extend([
            "## Consensus Findings (All CLIs Agree)",
            "",
            "These findings were identified by ALL reviewers - **highest confidence**.",
            ""
        ])

        for i, finding in enumerate(data["consensus"], 1):
            lines.extend(format_finding(finding, i))
    else:
        lines.extend([
            "## Consensus Findings",
            "",
            "*No findings where all CLIs agreed.*",
            "",
            "---",
            ""
        ])

    # Majority findings
    if data["majority"]:
        lines.extend([
            "## Majority Findings (2+ CLIs Agree)",
            "",
            "These findings were identified by most reviewers - **likely valid**.",
            ""
        ])

        for i, finding in enumerate(data["majority"], 1):
            lines.extend(format_finding(finding, i))
    else:
        lines.extend([
            "## Majority Findings",
            "",
            "*No findings where 2+ CLIs agreed.*",
            "",
            "---",
            ""
        ])

    # Unique findings
    if any(data["unique"].values()):
        lines.extend([
            "## Unique Findings",
            "",
            "These findings were only identified by one reviewer - **may need human review**.",
            ""
        ])

        for cli, findings in data["unique"].items():
            if findings:
                lines.extend([
                    f"### {cli.upper()} Only ({len(findings)} findings)",
                    ""
                ])
                for i, finding in enumerate(findings[:10], 1):  # Limit to 10
                    lines.extend(format_unique_finding(finding, i))
                if len(findings) > 10:
                    lines.append(f"*... and {len(findings) - 10} more*")
                lines.append("")
    else:
        lines.extend([
            "## Unique Findings",
            "",
            "*No unique findings - all findings had agreement.*",
            ""
        ])

    # Footer
    lines.extend([
        "---",
        "",
        "*Generated by multi-ai-review plugin*"
    ])

    return "\n".join(lines)


def format_json_report(data: dict) -> str:
    """Generate a JSON report."""
    return json.dumps(data, indent=2, default=str)


def format_section(data: dict, section: str) -> str:
    """Format only a specific section."""
    if section == "consensus":
        if not data["consensus"]:
            return "No consensus findings."
        lines = ["## Consensus Findings", ""]
        for i, finding in enumerate(data["consensus"], 1):
            lines.extend(format_finding(finding, i))
        return "\n".join(lines)

    elif section == "majority":
        if not data["majority"]:
            return "No majority findings."
        lines = ["## Majority Findings", ""]
        for i, finding in enumerate(data["majority"], 1):
            lines.extend(format_finding(finding, i))
        return "\n".join(lines)

    elif section == "unique":
        if not any(data["unique"].values()):
            return "No unique findings."
        lines = ["## Unique Findings", ""]
        for cli, findings in data["unique"].items():
            if findings:
                lines.append(f"### {cli.upper()} ({len(findings)} findings)")
                lines.append("")
                for i, finding in enumerate(findings, 1):
                    lines.extend(format_unique_finding(finding, i))
                lines.append("")
        return "\n".join(lines)

    return "Unknown section."


def main():
    parser = argparse.ArgumentParser(description="Format review report")
    parser.add_argument("--review", "-r", required=True, help="Review ID")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--section", "-s",
                        choices=["all", "consensus", "majority", "unique"],
                        default="all")
    parser.add_argument("--debug", action="store_true", help="Show detailed error messages")

    args = parser.parse_args()

    try:
        data = aggregate_findings(args.review)

        if args.format == "json":
            print(format_json_report(data))
        elif args.section != "all":
            print(format_section(data, args.section))
        else:
            print(format_markdown_report(data))

    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
