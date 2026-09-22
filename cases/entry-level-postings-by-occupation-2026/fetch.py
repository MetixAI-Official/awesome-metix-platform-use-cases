#!/usr/bin/env python3
"""Reproduce this study: how much of each occupation's open US postings is open to someone starting out.

    export METIX_KEY=...   (your key; or put it in the repository's .env)
    python3 cases/entry-level-postings-by-occupation-2026/fetch.py

Count queries only, one Credit each: no posting is read. The families, their
order, and their audits are in queries/families.json; what is counted is in
queries/measures.json. A count of 100,000 or more comes back banded and cannot
be divided, so a banded count is redone as the sum of the family's title parts
(the registered nurse family has two). Every family total is counted first, so
a banded count that cannot be split stops the run before the rest is spent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import Platform, aggregate, write_json

FAMILIES = json.loads((HERE / "queries" / "families.json").read_text(encoding="utf-8"))[
    "families"
]
MEASURES = json.loads((HERE / "queries" / "measures.json").read_text(encoding="utf-8"))
SRC = "queries/families.json · queries/measures.json"
MIN_BASE = 30  # a share is published only when its denominator is at least 30

LABEL = MEASURES["label"]
REQ = MEASURES["requirement"]
DOOR = {"field": LABEL["field"], "in": LABEL["door"]}
STATED = {"field": REQ["field"], "exists": True}
EARLY = {"field": REQ["field"], "lte": REQ["door_max_months"]}

# What each family row counts, as conditions added to the family's own.
FAMILY_MEASURES = {
    **{
        key: [{"field": LABEL["field"], "eq": value}]
        for key, value in LABEL["counted"].items()
    },
    "stated_count": [STATED],
    "stated_le24_count": [EARLY],
    "door_stated_count": [DOOR, STATED],
    "door_le24_count": [DOOR, EARLY],
}
SUBGROUP_MEASURES = {
    "label_door_count": [DOOR],
    "stated_count": [STATED],
    "stated_le24_count": [EARLY],
}


def titles(words: list[str]) -> dict:
    return {"any": [{"field": "title", "match": w} for w in words]}


def inside(family: dict) -> list[dict]:
    """A posting's title belongs to the family, before precedence."""
    conditions = [titles(family["terms"])]
    if family.get("also"):
        conditions.append(titles(family["also"]))
    if family.get("exclude"):
        conditions.append({"not": titles(family["exclude"])})
    return conditions


def outside(family: dict) -> dict:
    """The negation of inside(), written flat to stay within the nesting limit."""
    options = [{"not": titles(family["terms"])}]
    if family.get("also"):
        options.append({"not": titles(family["also"])})
    if family.get("exclude"):
        options.append(titles(family["exclude"]))
    return {"any": options}


def membership(i: int) -> list[dict]:
    """Family i under precedence: its own terms, and in no family before it."""
    earlier = FAMILIES[:i]
    simple = [f for f in earlier if not f.get("also") and not f.get("exclude")]
    conditions = inside(FAMILIES[i]) + MEASURES["base"]
    if simple:
        conditions.append({"not": titles([w for f in simple for w in f["terms"]])})
    return conditions + [
        outside(f) for f in earlier if f.get("also") or f.get("exclude")
    ]


def parts(family: dict) -> list[list[dict]]:
    """Disjoint title parts that add up to the family, each below the band."""
    out = []
    for j, words in enumerate(family.get("parts", [])):
        before = [w for part in family["parts"][:j] for w in part]
        out.append([titles(words)] + ([{"not": titles(before)}] if before else []))
    return out


def count(p: Platform, family: dict, conditions: list[dict]) -> int:
    """One count; when it comes back banded, the family's parts are counted and added."""
    n = p.count("jobs", {"all": conditions})
    if isinstance(n, int):
        return n
    split = [p.count("jobs", {"all": conditions + part}) for part in parts(family)]
    if not split or not all(isinstance(x, int) for x in split):
        sys.exit(
            f"Not written: a count for {family['id']} came back banded ({n}). "
            "Give the family parts in queries/families.json."
        )
    return sum(split)


def share(part: int, whole: int) -> float | None:
    return round(part / whole, 4) if whole >= MIN_BASE else None


def family_row(family: dict, c: dict) -> dict:
    door = c["internship_count"] + c["entry_count"]
    labelled = door + c["associate_count"] + c["not_applicable_count"]
    label_only = c["door_stated_count"] - c["door_le24_count"]
    requirement_only = c["stated_le24_count"] - c["door_le24_count"]
    agree_not = c["stated_count"] - c["stated_le24_count"] - label_only
    return {
        "group": family["id"],
        "label": family["label"],
        "paper_quintiles": (family.get("paper") or {}).get("quintiles"),
        **c,
        "other_label_count": c["total_count"] - labelled,
        "label_door_count": door,
        "label_door_share": share(door, c["total_count"]),
        "door_internship_share": share(c["internship_count"], door),
        "associate_share": share(c["associate_count"], c["total_count"]),
        "not_applicable_share": share(c["not_applicable_count"], c["total_count"]),
        "stated_share": share(c["stated_count"], c["total_count"]),
        "requirement_door_share": share(c["stated_le24_count"], c["stated_count"]),
        "label_door_among_stated_share": share(
            c["door_stated_count"], c["stated_count"]
        ),
        "agree_door_count": c["door_le24_count"],
        "label_only_count": label_only,
        "requirement_only_count": requirement_only,
        "agree_not_door_count": agree_not,
        "disagree_share": share(label_only + requirement_only, c["stated_count"]),
        "label_door_over_24_share": share(label_only, c["door_stated_count"]),
    }


def subgroup_row(group: str, c: dict, of: str, note: str) -> dict:
    row = {"group": group, "family": of, **c}
    row["label_door_share"] = share(c["label_door_count"], c["total_count"])
    if "stated_count" in c:
        row["stated_share"] = share(c["stated_count"], c["total_count"])
    if "stated_le24_count" in c:
        row["requirement_door_share"] = share(c["stated_le24_count"], c["stated_count"])
    row["note"] = note
    return row


def main() -> int:
    p = Platform(max_credits=140)
    snap = p.snapshot
    index = {f["id"]: i for i, f in enumerate(FAMILIES)}

    # 1. Every total first, so a banded one stops the run before the rest is spent.
    totals = {f["id"]: count(p, f, membership(i)) for i, f in enumerate(FAMILIES)}

    # 2. Labels and requirements for each study family.
    rows = []
    for i, family in enumerate(FAMILIES):
        if family["role"] != "study":
            continue
        c = {"total_count": totals[family["id"]]}
        for key, extra in FAMILY_MEASURES.items():
            c[key] = count(p, family, membership(i) + extra)
        rows.append(family_row(family, c))
    # 3. Subgroups: AI training work, AI-titled software, customer service outside
    #    store industries, and travel nursing.
    sub = []
    ai_training = FAMILIES[index["ai-training"]]
    sub.append(
        subgroup_row(
            "ai-training",
            {
                "total_count": totals["ai-training"],
                "label_door_count": count(
                    p, ai_training, membership(index["ai-training"]) + [DOOR]
                ),
            },
            "ai-training",
            "Taken out of every family; see queries/families.json.",
        )
    )
    for spec in MEASURES["subgroups"]:
        i = index[spec["family"]]
        family = FAMILIES[i]
        extra = []
        if "title_terms_from" in spec:
            extra.append(titles(FAMILIES[index[spec["title_terms_from"]]]["terms"]))
        if "title_terms" in spec:
            extra.append(titles(spec["title_terms"]))
        if "not_industries" in spec:
            extra.append(
                {
                    "not": {
                        "any": [
                            {"field": "industries", "match": t}
                            for t in spec["not_industries"]
                        ]
                    }
                }
            )
        c = {"total_count": count(p, family, membership(i) + extra)}
        for key, more in SUBGROUP_MEASURES.items():
            c[key] = count(p, family, membership(i) + extra + more)
        sub.append(subgroup_row(spec["id"], c, spec["family"], spec["note"]))

        # The rest of the family, by subtraction: the same columns, no extra Credits.
        whole = next(r for r in rows if r["group"] == spec["family"])
        sub.append(
            subgroup_row(
                spec["rest_id"],
                {key: whole[key] - n for key, n in c.items()},
                spec["family"],
                f"The {spec['family']} family minus {spec['id']}, by subtraction.",
            )
        )
    # 4. Write only once every count is in, so a stopped run leaves data/ as it was.
    write_json(
        HERE,
        "families.json",
        aggregate(
            "jobs",
            snap,
            SRC,
            rows,
            base="Open job postings in the United States, one family per posting",
            note=(
                "The label door is the share of all postings labelled Internship or "
                "Entry level. The requirement door is the share of postings stating "
                "an experience requirement that ask for 24 months or less; "
                "stated_share is how many state one. The four agreement counts split "
                "the postings that state a requirement by both measures. "
                "paper_quintiles copies the exposure quintile the cited paper gives "
                "the matching occupation (queries/families.json); null has none."
            ),
        ),
    )

    write_json(
        HERE,
        "subgroups.json",
        aggregate(
            "jobs",
            snap,
            SRC,
            sub,
            base="Open job postings in the United States",
            note=(
                "Each subgroup is part of the family named in family; the row after "
                "it is the rest of that family, by subtraction. ai-titled-software is "
                "part of the ai family, so its rest row is the ai family without "
                "software terms; the software family row in families.json holds "
                "software titles with no AI term."
            ),
        ),
    )

    write_json(HERE, "receipt.json", p.receipt())
    print(f"{p.calls} calls, {p.spent()} Credits")
    for r in rows:
        print(
            f"{r['group']:18} n={r['total_count']:6} label door {r['label_door_share']}"
            f" stated {r['stated_share']} requirement door {r['requirement_door_share']}"
        )
    for r in sub:
        print(r["group"], r["total_count"], r["label_door_share"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
