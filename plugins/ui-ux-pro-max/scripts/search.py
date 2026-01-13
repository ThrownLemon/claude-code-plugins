#!/usr/bin/env python3
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]

Domains: style, prompt, color, chart, landing, product, ux, typography, icons
Stacks: html-tailwind, react, nextjs, nuxtjs, nuxt-ui, vue, svelte, swiftui, react-native, flutter, shadcn
"""

import sys
import io

# Fix UnicodeEncodeError on Windows (cp1252 doesn't support Unicode symbols)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return "Error: {}".format(result['error'])

    output = []
    if result.get("stack"):
        output.append("## UI Pro Max Stack Guidelines")
        output.append("**Stack:** {} | **Query:** {}".format(result['stack'], result['query']))
    else:
        output.append("## UI Pro Max Search Results")
        output.append("**Domain:** {} | **Query:** {}".format(result['domain'], result['query']))
    output.append("**Source:** {} | **Found:** {} results\n".format(result['file'], result['count']))

    for i, row in enumerate(result['results'], 1):
        output.append("### Result {}".format(i))
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > 300:
                value_str = value_str[:300] + "..."
            output.append("- **{}:** {}".format(key, value_str))
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Stack-specific search (html-tailwind, react, nextjs, nuxtjs, nuxt-ui, vue, svelte, swiftui, react-native, flutter, shadcn)")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Stack search takes priority
    if args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
    else:
        result = search(args.query, args.domain, args.max_results)

    if args.json:
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_output(result))
