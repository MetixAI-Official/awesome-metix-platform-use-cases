#!/usr/bin/env python3
"""Rerun this card: the posted pay floor of US inference roles that state a salary.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/us-inference-pay-2026/fetch.py

Count queries only: postings that state a USD salary, then how many have an
annual minimum at or above each threshold. Bands are the differences.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, load_query, write_json

THRESHOLDS = [150_000, 200_000, 250_000, 300_000]


def main() -> int:
    platform = Platform(max_credits=20)
    where = load_query(HERE, "us-inference-usd")["where"]
    stated = platform.count("jobs", where)
    at_least = [
        platform.count(
            "jobs", {"all": [where, {"field": "salary.annual_min", "gte": t}]}
        )
        for t in THRESHOLDS
    ]
    # Every US posting with the same title filter, to show how many state pay at all.
    role_filter = {
        "all": [c for c in where["all"] if c.get("field", "").split(".")[0] != "salary"]
    }
    us_total = platform.count("jobs", role_filter)

    edges = [0, *THRESHOLDS]
    counts = [stated - at_least[0]] + [
        at_least[i] - at_least[i + 1] for i in range(len(THRESHOLDS) - 1)
    ]
    counts.append(at_least[-1])
    rows = [
        {
            "group": f"{lo // 1000}k+"
            if i == len(edges) - 1
            else f"{lo // 1000}k-{edges[i + 1] // 1000}k",
            "min_usd": lo,
            "count": n,
        }
        for i, (lo, n) in enumerate(zip(edges, counts))
    ]
    rows[0]["group"] = f"under-{THRESHOLDS[0] // 1000}k"
    write_json(
        HERE,
        "bands.json",
        aggregate(
            "jobs",
            platform.snapshot,
            "queries/us-inference-usd.json",
            rows,
            stated_count=stated,
            us_postings_count=us_total,
        ),
    )
    write_json(HERE, "receipt.json", platform.receipt())
    print(stated, "of", us_total, rows, f"{platform.spent()} Credits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
