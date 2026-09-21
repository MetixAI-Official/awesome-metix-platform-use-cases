#!/usr/bin/env python3
"""Rerun this card: open postings whose description names an AI coding tool.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/ai-coding-tools-in-postings-2026/fetch.py

Count queries only, one Credit each. Cursor, Codex, and Windsurf are counted
only when another AI coding tool is named in the same description; the plain
word counts are kept alongside for comparison.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, load_query, write_json

TOOLS = ["claude-code", "cursor", "github-copilot", "codex", "windsurf"]
WORD_ONLY = {
    "cursor": "cursor-word",
    "codex": "codex-word",
    "windsurf": "windsurf-word",
}
US = {"field": "location.country", "eq": "United States"}


def main() -> int:
    platform = Platform(max_credits=20)
    rows = []
    for tool in TOOLS:
        where = load_query(HERE, tool)["where"]
        row = {
            "group": tool,
            "count": platform.count("jobs", where),
            "us_count": platform.count("jobs", {"all": [where, US]}),
        }
        if tool in WORD_ONLY:
            row["word_count"] = platform.count(
                "jobs", load_query(HERE, WORD_ONLY[tool])["where"]
            )
        rows.append(row)
    rows.sort(key=lambda r: -r["count"])
    any_tool = platform.count("jobs", load_query(HERE, "any-tool")["where"])
    write_json(
        HERE,
        "tools.json",
        aggregate(
            "jobs",
            platform.snapshot,
            "queries/<tool>.json",
            rows,
            any_tool_count=any_tool,
        ),
    )
    write_json(HERE, "receipt.json", platform.receipt())
    print(
        {row["group"]: row["count"] for row in rows},
        "any:",
        any_tool,
        f"{platform.spent()} Credits",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
