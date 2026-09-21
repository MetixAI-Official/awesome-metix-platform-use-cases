#!/usr/bin/env python3
"""Rerun this case on your own Metix AI Platform key.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/inference-roles-us-metros-2026/fetch.py

Runs the queries in queries/, reads the matching US postings, collapses
same-city reposts, groups the rest by metro (metros.json), and writes the
aggregates and the run receipt to data/. The postings themselves go to
data/raw/, which git ignores. The run stops before any call that could take it
past MAX_CREDITS (default 150).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, load_query, write_json

DETAIL_FIELDS = ["title", "company.name", "location.city", "location.state"]
US_STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
    "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming", "United States",
}  # fmt: skip


def metro_index() -> dict[tuple[str | None, str | None], str]:
    config = json.loads((HERE / "metros.json").read_text(encoding="utf-8"))
    index: dict[tuple[str | None, str | None], str] = {}
    for metro in config["metros"]:
        for state, cities in metro["cities"].items():
            for city in cities:
                index[(city, state)] = metro["id"]
        for city in metro.get("city_only", []):
            index[(city, None)] = metro["id"]
    return index


def place(record: dict, index: dict) -> str:
    location = record.get("location") or {}
    city, state = location.get("city"), location.get("state")
    if (city, state) in index:
        return index[(city, state)]
    if not city or city in US_STATES:
        return "no-city"
    return "elsewhere"


def distinct(records: list[dict]) -> list[dict]:
    """One posting per title, company, and city: a same-city repost counts once."""
    seen: set[tuple] = set()
    kept = []
    for record in records:
        location = record.get("location") or {}
        title = re.sub(r"\s+", " ", (record.get("title") or "").strip().lower())
        key = (
            title,
            (record.get("company") or {}).get("name"),
            location.get("city"),
            location.get("state"),
        )
        if key not in seen:
            seen.add(key)
            kept.append(record)
    return kept


def main() -> int:
    platform = Platform(max_credits=150)
    snap = platform.snapshot

    world = platform.count("jobs", load_query(HERE, "world-total")["where"])
    ids, us_total = platform.search_all("jobs", load_query(HERE, "us-postings"))
    records = platform.detail("jobs", ids, DETAIL_FIELDS)
    raw = HERE / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "postings.json").write_text(
        json.dumps(records, ensure_ascii=False), encoding="utf-8"
    )

    kept = distinct(records)
    index = metro_index()
    by_metro = Counter(place(r, index) for r in kept)
    residual = {"elsewhere", "no-city"}
    order = [m for m, _ in by_metro.most_common() if m not in residual] + [
        "elsewhere",
        "no-city",
    ]
    rows = [
        {
            "group": m,
            "count": by_metro.get(m, 0),
            "share": round(by_metro.get(m, 0) / len(kept), 4),
        }
        for m in order
    ]
    write_json(
        HERE, "metros.json", aggregate("jobs", snap, "queries/us-postings.json", rows)
    )

    companies = Counter((r.get("company") or {}).get("name") or "Unknown" for r in kept)
    top = [{"company": c, "count": n} for c, n in companies.most_common(5)]
    write_json(
        HERE, "companies.json", aggregate("jobs", snap, "queries/us-postings.json", top)
    )
    context = [
        {"group": "world-postings", "count": world},
        {"group": "us-postings", "count": us_total},
        {"group": "us-records-read", "count": len(records)},
        {"group": "us-distinct-postings", "count": len(kept)},
        {"group": "us-companies", "count": len(companies)},
    ]
    write_json(
        HERE,
        "context.json",
        aggregate("jobs", snap, "queries/world-total.json", context),
    )
    write_json(HERE, "receipt.json", platform.receipt())
    print(
        f"{len(kept)} distinct US postings; {platform.calls} calls; {platform.spent()} Credits."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
