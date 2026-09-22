"""A small client for the public Metix AI Platform API, shared by every case's fetch.py.

Standard library only. The key comes from METIX_KEY, or from the repository's
.env, and is never printed. Every call is counted, and the receipt's Credits
come from GET /auth/key/status before and after the run.
"""

from __future__ import annotations

import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://mira-api.metix.ai"
REPO = Path(__file__).resolve().parents[1]
MIN_CELL = 10

ENTITIES = {
    "jobs": ("/v1/jobs/query", "/entity/v1/jobs/detail-by-id", "job_ids"),
    "people": ("/v1/people/query", "/entity/v1/profiles/detail-by-id", "profile_ids"),
    "companies": (
        "/v1/companies/query",
        "/entity/v1/companies/detail-by-id",
        "company_ids",
    ),
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
    # The site's setup step shows a placeholder of x's; sending it would fail with a 401
    # that does not say why.
    prefix, _, rest = key.partition("_")
    if prefix == "metix" and rest and set(rest) <= {"x"}:
        sys.exit(
            "METIX_KEY still holds the placeholder. Replace it with your own key from"
            " https://platform.metix.ai/api-keys."
        )
    return key


class Platform:
    def __init__(self, max_credits: int | None = None) -> None:
        self.key = load_key()
        self.max_credits = max_credits or int(os.environ.get("MAX_CREDITS", "300"))
        self.calls = (
            0  # search and detail calls; the free balance reads are not counted
        )
        self.results = 0
        self.records = 0
        self.ceiling_used = 0  # the most the calls so far could have cost
        self.ran_at = datetime.now(timezone.utc).replace(microsecond=0)
        self.start_balance = self.remaining()

    # -- transport -------------------------------------------------------

    def request(
        self, method: str, path: str, body: dict | None = None, *, billable: bool = True
    ) -> dict:
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
        self.calls += billable
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.load(resp)["data"]
        except urllib.error.HTTPError as err:
            detail = json.loads(err.read() or b"{}")
            sys.exit(
                f"{method} {path} failed: {err.code} "
                f"{detail.get('error_code')}: {detail.get('msg')}"
            )

    def remaining(self) -> int:
        # Free route. Only the balance is read; the rest of the response is ignored.
        status = self.request("GET", "/auth/key/status", billable=False)
        return status["user_quota"]["quota_remaining"]

    def spent(self) -> int:
        return self.start_balance - self.remaining()

    def _guard(self, most: int) -> None:
        # A call is charged per result returned, so `most` is its worst case. Stop
        # before the worst case of the run could pass the ceiling.
        if self.ceiling_used + most > self.max_credits:
            sys.exit(
                f"Stopping: this call could take the run past {self.max_credits} Credits "
                "(set MAX_CREDITS to raise the ceiling)."
            )
        self.ceiling_used += most

    # -- search and detail ----------------------------------------------

    def count(self, entity: str, where: dict) -> int | str:
        """The match total for a Query Spec, for at most 1 Credit.

        Exact below the banding threshold on GET /contract; a string such as
        "100000+" above it.
        """
        self._guard(1)
        page = self.request("POST", ENTITIES[entity][0], {"where": where, "size": 1})
        self.results += len(page.get(ENTITIES[entity][2], []))
        return page.get("total", 0)

    def search_all(self, entity: str, spec: dict) -> tuple[list[str], int | str]:
        path, _, id_key = ENTITIES[entity]
        # Count first (1 Credit) so the guard sees what the pages will really return.
        total = self.count(entity, spec["where"])
        left = total if isinstance(total, int) else 100_000
        ids: list[str] = []
        body = dict(spec)
        while True:
            self._guard(math.ceil(min(body.get("size", 100), left) / 25))
            page = self.request("POST", path, body)
            ids += page.get(id_key, [])
            self.results += len(page.get(id_key, []))
            left -= len(page.get(id_key, []))
            if not page.get("next"):
                return ids, page.get("total", len(ids))
            body = {**spec, "after": page["next"]}

    def detail(self, entity: str, ids: list[str], fields: list[str]) -> list[dict]:
        _, path, id_key = ENTITIES[entity]
        records: list[dict] = []
        for start in range(0, len(ids), 100):
            batch = ids[start : start + 100]
            self._guard(math.ceil(len(batch) / 5))
            page = self.request("POST", path, {id_key: batch, "_source": fields})
            found = page.get("results", [])
            self.records += len(found)
            records += found
        return records

    # -- outputs ---------------------------------------------------------

    @property
    def snapshot(self) -> str:
        return self.ran_at.date().isoformat()

    def receipt(self) -> dict:
        return {
            "ran_at": self.ran_at.isoformat().replace("+00:00", "Z"),
            "calls": self.calls,
            "results": self.results,
            "records": self.records,
            "credits": self.spent(),
            "credits_source": "GET /auth/key/status before and after the run",
        }


def suppress(n: int | str, k: int = MIN_CELL) -> int | str:
    """A count of people below k is published as "<k"."""
    if isinstance(n, int) and 0 < n < k:
        return f"<{k}"
    return n


def load_query(case_dir: Path, name: str) -> dict:
    return json.loads(
        (case_dir / "queries" / f"{name}.json").read_text(encoding="utf-8")
    )


def write_json(case_dir: Path, name: str, doc: dict) -> None:
    out = case_dir / "data" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def aggregate(
    unit: str, snapshot: str, query: str, rows: list[dict], **extra: object
) -> dict:
    return {"unit": unit, "snapshot": snapshot, "query": query, **extra, "rows": rows}
