#!/usr/bin/env python3
"""Rerun this card: open postings by model-lifecycle stage named in the job title.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/model-lifecycle-titles-2026/fetch.py

Eight count queries, one Credit each: every stage worldwide and in the US.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, load_query, write_json

STAGES = ["pre-training", "post-training", "fine-tuning", "inference"]
US = {"field": "location.country", "eq": "United States"}


def main() -> int:
    platform = Platform(max_credits=20)
    rows = []
    for stage in STAGES:
        where = load_query(HERE, stage)["where"]
        world = platform.count("jobs", where)
        us = platform.count("jobs", {"all": [where, US]})
        rows.append({"group": stage, "count": world, "us_count": us})
    write_json(
        HERE,
        "stages.json",
        aggregate("jobs", platform.snapshot, "queries/<stage>.json", rows),
    )
    write_json(HERE, "receipt.json", platform.receipt())
    print({row["group"]: row["count"] for row in rows}, f"{platform.spent()} Credits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
