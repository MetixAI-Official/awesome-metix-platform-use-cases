#!/usr/bin/env python3
"""Rerun this case on your own Metix AI Platform key.

    export METIX_KEY=metix_xxxxxxxxxxxx   (or put it in the repository's .env)
    python3 cases/inference-roles-us-metros-2026/fetch.py

Runs the queries in queries/, reads the matching US postings, collapses
same-city reposts, groups the rest by metro (metros.json), and writes the
aggregates and the run receipt to data/. The postings themselves go to
data/raw/, which git ignores. Standard library only; the key is never printed.

A run stops before reading records if it would cost more than MAX_CREDITS
(default 150).
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

API = "https://mira-api.metix.ai"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "data"
MAX_CREDITS = int(os.environ.get("MAX_CREDITS", "150"))
DETAIL_FIELDS = ["title", "company.name", "location.city", "location.state"]
US_STATES = {
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
    "United States",
}


def load_key() -> str:
    key = os.environ.get("METIX_KEY", "").strip()
    env_file = REPO / ".env"
    if not key and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "METIX_KEY":
                key = value.strip().strip("\"'")
    if not key:
        sys.exit(
            "METIX_KEY is not set. Create a key at https://platform.metix.ai/api-keys."
        )
    return key


class Client:
    def __init__(self, key: str) -> None:
        self.key = key
        self.calls = 0

    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            API + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )
        self.calls += 1
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)["data"]
        except urllib.error.HTTPError as err:
            detail = json.loads(err.read() or b"{}")
            sys.exit(
                f"{method} {path} failed: {err.code} {detail.get('error_code')}: {detail.get('msg')}"
            )

    def remaining(self) -> int:
        # Free route. Only the balance is read; the rest of the response is ignored.
        return self.request("GET", "/auth/key/status")["user_quota"]["quota_remaining"]


def query(name: str) -> dict:
    return json.loads((HERE / "queries" / f"{name}.json").read_text(encoding="utf-8"))


def search_all(client: Client, spec: dict) -> tuple[list[str], int]:
    ids: list[str] = []
    body = dict(spec)
    while True:
        page = client.request("POST", "/v1/jobs/query", body)
        ids += page.get("job_ids", [])
        if not page.get("next"):
            return ids, page.get("total", len(ids))
        body = {**spec, "after": page["next"]}


def read_postings(client: Client, ids: list[str]) -> list[dict]:
    records: list[dict] = []
    for start in range(0, len(ids), 100):
        batch = {"job_ids": ids[start : start + 100], "_source": DETAIL_FIELDS}
        records += client.request("POST", "/entity/v1/jobs/detail-by-id", batch).get(
            "results", []
        )
    return records


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


def write(name: str, doc: dict) -> None:
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    client = Client(load_key())
    before = client.remaining()
    ran_at = datetime.now(timezone.utc).replace(microsecond=0)
    snapshot = ran_at.date().isoformat()

    world = client.request("POST", "/v1/jobs/query", query("world-total"))
    ids, us_total = search_all(client, query("us-postings"))
    projected = (
        1
        + math.ceil(len(ids) / 25)
        + sum(math.ceil(min(100, len(ids) - i) / 5) for i in range(0, len(ids), 100))
    )
    if projected > MAX_CREDITS:
        sys.exit(
            f"Stopping before reading records: this run would cost about {projected} Credits (MAX_CREDITS={MAX_CREDITS})."
        )

    records = read_postings(client, ids)
    (DATA / "raw").mkdir(parents=True, exist_ok=True)
    (DATA / "raw" / "postings.json").write_text(
        json.dumps(records, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    kept = distinct(records)
    index = metro_index()
    by_metro = Counter(place(r, index) for r in kept)
    order = [
        m for m, _ in by_metro.most_common() if m not in {"elsewhere", "no-city"}
    ] + ["elsewhere", "no-city"]
    rows = [
        {
            "group": m,
            "count": by_metro.get(m, 0),
            "share": round(by_metro.get(m, 0) / len(kept), 4),
        }
        for m in order
    ]
    write(
        "metros.json",
        {
            "unit": "jobs",
            "snapshot": snapshot,
            "query": "queries/us-postings.json",
            "rows": rows,
        },
    )

    companies = Counter((r.get("company") or {}).get("name") or "Unknown" for r in kept)
    write(
        "companies.json",
        {
            "unit": "jobs",
            "snapshot": snapshot,
            "query": "queries/us-postings.json",
            "rows": [{"company": c, "count": n} for c, n in companies.most_common(5)],
        },
    )
    write(
        "context.json",
        {
            "unit": "jobs",
            "snapshot": snapshot,
            "query": "queries/world-total.json",
            "rows": [
                {"group": "world-postings", "count": world.get("total")},
                {"group": "us-postings", "count": us_total},
                {"group": "us-records-read", "count": len(records)},
                {"group": "us-distinct-postings", "count": len(kept)},
                {"group": "us-companies", "count": len(companies)},
            ],
        },
    )

    after = client.remaining()
    write(
        "receipt.json",
        {
            "ran_at": ran_at.isoformat().replace("+00:00", "Z"),
            "calls": client.calls,
            "results": len(world.get("job_ids", [])) + len(ids),
            "records": len(records),
            "credits": before - after,
            "credits_source": "GET /auth/key/status before and after the run",
        },
    )
    print(
        f"{len(kept)} distinct US postings in {len(rows) - 2} metros; {before - after} Credits."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
