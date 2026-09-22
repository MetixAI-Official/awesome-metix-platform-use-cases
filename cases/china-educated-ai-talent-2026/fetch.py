#!/usr/bin/env python3
"""Reproduce this study: AI staff at ten labs whose bachelor's degree is from a mainland-China institution.

    export METIX_KEY=...   (your key; or put it in the repository's .env)
    python3 cases/china-educated-ai-talent-2026/fetch.py

Count queries only, one Credit each: no profile record is read. Who counts is
in queries/population.json, the institution list in queries/institutions.json.
Every count of people passes the small-cell rule, and the run stops before
writing anything if a published total would let a reader subtract their way
to a count of 1 to 9 people.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import MIN_CELL, Platform, aggregate, suppress, write_json

POP = json.loads((HERE / "queries" / "population.json").read_text(encoding="utf-8"))
INST = json.loads((HERE / "queries" / "institutions.json").read_text(encoding="utf-8"))
SRC_POP = "queries/population.json"
SRC_BOTH = "queries/population.json · queries/institutions.json"
COUNTRY_NOTE = (
    "Where people in AI roles with a mainland-China bachelor's list themselves, "
    "by the profile's location.country. Almost no profile lists China: only 32 "
    "AI-role profiles do, and people whose current job is recorded in China "
    "mostly list another country. The China row therefore does not measure how "
    "many live in China, and nothing here measures how many work there."
)

CURRENT = {"field": "experience.is_current", "eq": True}
AI_TITLE = {
    "any": [{"field": "experience.title", "match": t} for t in POP["ai_title_terms"]]
}
RESEARCH = {
    "any": [
        {"field": "experience.title", "match": t} for t in POP["research_title_terms"]
    ]
}
RECENT = {"field": "experience.start_date", "gte": POP["recent_hire_window"]}
US = POP["us"]
BACHELOR = {"field": "education.degree", "eq": "Bachelor"}


def school(
    match: list[str], exact: list[str], exclude: list[str] | None = None
) -> list[dict]:
    """The school conditions for one has_education entry: any listed name, none of the exclude words.

    The Platform matches names word by word, so a longer name that contains a
    listed one matches too; the exclude words remove the ones that belong elsewhere.
    """
    options = [{"field": "education.school.name", "match": t} for t in match]
    if exact:
        options.append({"field": "education.school.name", "in": exact})
    conditions = [{"any": options}]
    if exclude:
        conditions.append(
            {
                "not": {
                    "any": [
                        {"field": "education.school.name", "match": t} for t in exclude
                    ]
                }
            }
        )
    return conditions


ANY_BACHELOR = {"has_education": {"all": [BACHELOR]}}
MAINLAND = {
    "has_education": {
        "all": [BACHELOR, *school(INST["match"], INST["exact"], INST["exclude"])]
    }
}


def ai_job(companies: list[str] | None = None, *extra: dict) -> dict:
    """One current job with an AI title, optionally at named companies, in one entry."""
    conditions = [CURRENT, AI_TITLE]
    if companies:
        conditions.append({"field": "experience.company.name", "in": companies})
    return {"has_experience": {"all": conditions + list(extra)}}


def not_currently_at(companies: list[str]) -> dict:
    return {
        "not": {
            "has_experience": {
                "all": [CURRENT, {"field": "experience.company.name", "in": companies}]
            }
        }
    }


COLUMNS = (
    "us_visible_count",
    "us_bachelor_count",
    "us_mainland_count",
    "us_recent_bachelor_count",
    "us_recent_mainland_count",
    "us_research_bachelor_count",
    "us_research_mainland_count",
)
# Research cells are suppressed at some labs, so no ten-lab research total is published:
# the total minus the published labs would give the suppressed ones back.
SUMMED = COLUMNS[:5]


def lab_row(
    p: Platform, row_id: str, name: str, companies: list[str], earlier: list[str]
) -> dict:
    def n(*conditions: dict, extra: tuple[dict, ...] = ()) -> int:
        where = [ai_job(companies, *extra)]
        if earlier:
            where.append(not_currently_at(earlier))
        return p.count("people", {"all": where + list(conditions)})

    return {
        "group": row_id,
        "label": name,
        "us_visible_count": n(US),
        "us_bachelor_count": n(US, ANY_BACHELOR),
        "us_mainland_count": n(US, MAINLAND),
        "us_recent_bachelor_count": n(US, ANY_BACHELOR, extra=(RECENT,)),
        "us_recent_mainland_count": n(US, MAINLAND, extra=(RECENT,)),
        "us_research_bachelor_count": n(US, ANY_BACHELOR, extra=(RESEARCH,)),
        "us_research_mainland_count": n(US, MAINLAND, extra=(RESEARCH,)),
    }


def audit(rows: list[dict]) -> list[str]:
    """Counts of people a reader could derive by subtracting published cells, found before publishing.

    Rows are disjoint and the ten-lab row is their sum, so a cell is recoverable
    when it is the only suppressed one in a summed column. Within a lab, the
    earlier starters, the other titles, and the people with no Bachelor entry
    are differences of published cells.
    """
    small = lambda v: isinstance(v, int) and 0 < v < MIN_CELL
    problems = []
    for col in SUMMED:
        hidden = [r["group"] for r in rows if small(r[col])]
        if hidden:
            problems.append(
                f"{col}: {hidden} would be suppressed but the column has a total"
            )
    for r in rows:
        pairs = {
            "no bachelor": (r["us_visible_count"], r["us_bachelor_count"]),
            "earlier, bachelor": (
                r["us_bachelor_count"],
                r["us_recent_bachelor_count"],
            ),
            "earlier, mainland": (
                r["us_mainland_count"],
                r["us_recent_mainland_count"],
            ),
            "other titles, bachelor": (
                r["us_bachelor_count"],
                r["us_research_bachelor_count"],
            ),
            "other titles, mainland": (
                r["us_mainland_count"],
                r["us_research_mainland_count"],
            ),
            "bachelor, not mainland": (r["us_bachelor_count"], r["us_mainland_count"]),
        }
        for what, (whole, part) in pairs.items():
            if small(part):
                continue  # the part is suppressed, so the difference is not exact
            if small(whole - part):
                problems.append(f"{r['group']}: {what} = {whole - part}")
    return problems


def main() -> int:
    p = Platform(max_credits=150)
    snap = p.snapshot
    labs = POP["labs"]
    every_company = sorted({c for lab in labs for c in lab["companies"]})

    # 1. Each lab, disjoint: nobody who holds a current job at a lab listed earlier.
    rows = []
    for i, lab in enumerate(labs):
        earlier = sorted({c for prior in labs[:i] for c in prior["companies"]})
        rows.append(lab_row(p, lab["id"], lab["name"], lab["companies"], earlier))
    total = {"group": "ten-labs", "label": "The ten labs together"}
    total.update({col: sum(r[col] for r in rows) for col in SUMMED})

    problems = audit(rows)
    if problems:
        sys.exit(
            "Not written; these cells could be recovered:\n  " + "\n  ".join(problems)
        )
    published = [
        {k: suppress(v) if k in COLUMNS else v for k, v in r.items()} for r in rows
    ]
    write_json(
        HERE, "labs.json", aggregate("profiles", snap, SRC_BOTH, published + [total])
    )

    # 2. Institutions, at the ten labs, US-based: one institution per count.
    ten_us = [ai_job(every_company), US]
    schools = [
        school(i.get("match", []), i.get("exact", []), i.get("exclude", []))
        for i in POP["institutions"]
    ]
    inst_rows = [
        {
            "group": inst["id"],
            "label": inst["name"],
            "strict": bool(inst.get("exclude")),
            "count": suppress(
                p.count(
                    "people",
                    {"all": ten_us + [{"has_education": {"all": [BACHELOR, *cond]}}]},
                )
            ),
        }
        for inst, cond in zip(POP["institutions"], schools)
    ]
    # No union of the twelve: each guarded row nests a not inside an any, and a union of
    # them passes the Platform's nesting limit of 6. The rows are summed instead, so a person
    # with Bachelor entries at two of the twelve counts in both.
    row_sum = sum(r["count"] for r in inst_rows if isinstance(r["count"], int))
    write_json(
        HERE,
        "institutions.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            inst_rows,
            base="AI roles at the ten labs, US-based, with a Bachelor entry at the institution",
            rows_sum_count=row_sum,
        ),
    )

    # 3. Where AI-titled people with a mainland-China bachelor live now, any employer.
    everyone = [ai_job(), MAINLAND]
    world = p.count("people", {"all": everyone})
    located = p.count(
        "people", {"all": everyone + [{"field": "location.country", "exists": True}]}
    )
    countries = [
        {
            "group": c,
            "count": suppress(
                p.count(
                    "people",
                    {"all": everyone + [{"field": "location.country", "eq": c}]},
                )
            ),
        }
        for c in POP["countries"]
    ]
    listed = sum(r["count"] for r in countries if isinstance(r["count"], int))
    countries.append({"group": "rest-of-world", "count": suppress(located - listed)})
    countries.append({"group": "no-location", "count": suppress(world - located)})
    if sum(1 for r in countries if isinstance(r["count"], str)) == 1:
        sys.exit(
            "Not written; one suppressed country could be recovered from the world count."
        )
    write_json(
        HERE,
        "countries.json",
        aggregate(
            "profiles", snap, SRC_BOTH, countries, world_count=world, note=COUNTRY_NOTE
        ),
    )

    # 4. Context: every US-based AI role, the ten labs worldwide, and how visible China-based employers are.
    context = [
        {
            "group": "us-ai-bachelor",
            "count": suppress(p.count("people", {"all": [ai_job(), US, ANY_BACHELOR]})),
        },
        {
            "group": "us-ai-mainland",
            "count": suppress(p.count("people", {"all": [ai_job(), US, MAINLAND]})),
        },
        {
            "group": "ten-labs-world-bachelor",
            "count": suppress(
                p.count("people", {"all": [ai_job(every_company), ANY_BACHELOR]})
            ),
        },
        {
            "group": "ten-labs-world-mainland",
            "count": suppress(
                p.count("people", {"all": [ai_job(every_company), MAINLAND]})
            ),
        },
        {
            "group": "china-ai-visible",
            "count": suppress(
                p.count(
                    "people",
                    {"all": [ai_job(), {"field": "location.country", "eq": "China"}]},
                )
            ),
        },
    ]
    for org, names in (
        ("bytedance", ["ByteDance"]),
        ("alibaba", ["Alibaba Group", "Alibaba Cloud", "Alibaba"]),
        ("tencent", ["Tencent"]),
        ("baidu", ["Baidu"]),
        ("deepseek", ["DeepSeek"]),
    ):
        context.append(
            {
                "group": f"visible-ai-staff-{org}",
                "count": suppress(p.count("people", {"all": [ai_job(names)]})),
            }
        )
    write_json(HERE, "context.json", aggregate("profiles", snap, SRC_POP, context))

    write_json(HERE, "receipt.json", p.receipt())
    print(f"{p.calls} calls, {p.spent()} Credits")
    print({r["group"]: (r["us_mainland_count"], r["us_bachelor_count"]) for r in rows})
    print("ten labs:", total["us_mainland_count"], "of", total["us_bachelor_count"])
    print({r["group"]: r["count"] for r in inst_rows}, "rows sum", row_sum)
    return 0


if __name__ == "__main__":
    sys.exit(main())
