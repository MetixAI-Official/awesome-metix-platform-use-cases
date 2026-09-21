#!/usr/bin/env python3
"""Rerun this study: AI coding assistants and agent frameworks in job postings and profiles.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/ai-tool-stack-in-hiring-2026/fetch.py

Count queries only, one Credit each: no posting or profile record is read.
Tool conditions are in queries/tools.json, the other dimensions in
queries/dimensions.json. Every count of people passes the small-cell rule.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, suppress, write_json

TOOLS = json.loads((HERE / "queries" / "tools.json").read_text(encoding="utf-8"))[
    "tools"
]
DIMS = json.loads((HERE / "queries" / "dimensions.json").read_text(encoding="utf-8"))
US = DIMS["us"]


def both(*conditions: dict) -> dict:
    return {"all": list(conditions)}


def main() -> int:
    p = Platform(max_credits=150)
    snap = p.snapshot
    by_id = {t["id"]: t for t in TOOLS}
    assistants = [t for t in TOOLS if t["family"] == "assistant"]
    any_assistant = {"any": [t["postings"] for t in assistants]}

    # 1. Demand and supply for every tool, worldwide and in the US.
    demand, supply = [], []
    for t in TOOLS:
        demand.append(
            {
                "group": t["id"],
                "family": t["family"],
                "count": p.count("jobs", t["postings"]),
                "us_count": p.count("jobs", both(t["postings"], US)),
            }
        )
        supply.append(
            {
                "group": t["id"],
                "family": t["family"],
                "count": suppress(p.count("people", t["profiles"])),
                "us_count": suppress(p.count("people", both(t["profiles"], US))),
            }
        )
    write_json(
        HERE, "demand.json", aggregate("jobs", snap, "queries/tools.json", demand)
    )
    write_json(
        HERE, "supply.json", aggregate("profiles", snap, "queries/tools.json", supply)
    )

    # 2. How often two coding assistants are named in the same posting.
    pairs = [
        {
            "group": f"{a['id']}+{b['id']}",
            "count": p.count("jobs", both(a["postings"], b["postings"])),
        }
        for a, b in combinations(assistants, 2)
    ]
    write_json(
        HERE, "co-mentions.json", aggregate("jobs", snap, "queries/tools.json", pairs)
    )

    # 3. Postings naming any coding assistant: countries and industries.
    world = p.count("jobs", any_assistant)
    countries = [
        {
            "group": c,
            "count": p.count(
                "jobs", both(any_assistant, {"field": "location.country", "eq": c})
            ),
        }
        for c in DIMS["countries"]
    ]
    countries.append(
        {"group": "rest-of-world", "count": world - sum(r["count"] for r in countries)}
    )
    write_json(
        HERE,
        "countries.json",
        aggregate(
            "jobs", snap, "queries/dimensions.json", countries, world_count=world
        ),
    )
    industries = [
        {
            "group": i,
            "sector": sector,
            "count": p.count(
                "jobs", both(any_assistant, {"field": "industries", "match": i})
            ),
        }
        for sector in ("tech", "beyond")
        for i in DIMS["industries"][sector]
    ]
    write_json(
        HERE,
        "industries.json",
        aggregate(
            "jobs", snap, "queries/dimensions.json", industries, world_count=world
        ),
    )

    # 4. Posted pay floors in the US: postings naming any assistant against software engineer titles.
    pay = []
    for name, cond in (
        ("any-assistant", any_assistant),
        ("software-engineer", DIMS["pay_baseline"]),
    ):
        base = both(cond, US, DIMS["usd_stated"])
        stated = p.count("jobs", base)
        at_least = [
            p.count("jobs", both(base, {"field": "salary.annual_min", "gte": t}))
            for t in DIMS["pay_thresholds_usd"]
        ]
        pay.append(
            {
                "group": name,
                "count": stated,
                "at_least": dict(zip(map(str, DIMS["pay_thresholds_usd"]), at_least)),
            }
        )
    write_json(
        HERE, "pay.json", aggregate("jobs", snap, "queries/dimensions.json", pay)
    )

    write_json(HERE, "receipt.json", p.receipt())
    print(f"{p.calls} calls, {p.spent()} Credits; any assistant: {world}")
    print({r["group"]: (r["count"], by_id[r["group"]]["family"]) for r in demand})
    print({r["group"]: r["count"] for r in supply})
    return 0


if __name__ == "__main__":
    sys.exit(main())
