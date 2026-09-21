#!/usr/bin/env python3
"""Rerun this card: open forward-deployed engineering postings by country.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/forward-deployed-engineers-2026/fetch.py

One worldwide count plus one count per country in COUNTRIES, one Credit each.
Everything not in the list is reported as the rest of the world.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, load_query, write_json

# The twelve largest countries in a 500-posting read on the snapshot date.
COUNTRIES = [
    "United States",
    "India",
    "United Kingdom",
    "Germany",
    "Canada",
    "Netherlands",
    "France",
    "Spain",
    "Japan",
    "Australia",
    "Singapore",
    "Israel",
]


def main() -> int:
    platform = Platform(max_credits=20)
    where = load_query(HERE, "forward-deployed")["where"]
    world = platform.count("jobs", where)
    rows = []
    for country in COUNTRIES:
        n = platform.count(
            "jobs", {"all": [where, {"field": "location.country", "eq": country}]}
        )
        rows.append({"group": country, "count": n, "share": round(n / world, 4)})
    rows.sort(key=lambda r: -r["count"])
    rest = world - sum(r["count"] for r in rows)
    rows.append(
        {"group": "rest-of-world", "count": rest, "share": round(rest / world, 4)}
    )
    write_json(
        HERE,
        "countries.json",
        aggregate(
            "jobs",
            platform.snapshot,
            "queries/forward-deployed.json",
            rows,
            world_count=world,
        ),
    )
    write_json(HERE, "receipt.json", platform.receipt())
    print(world, rows[:3], f"{platform.spent()} Credits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
