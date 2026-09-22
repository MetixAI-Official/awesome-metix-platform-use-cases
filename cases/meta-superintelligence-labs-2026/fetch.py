#!/usr/bin/env python3
"""Reproduce this study: who makes up Meta Superintelligence Labs, as its own staff describe it.

    export METIX_KEY=...   (your key; or put it in the repository's .env)
    python3 cases/meta-superintelligence-labs-2026/fetch.py

Count queries only: each costs 1 Credit, or nothing when it finds no one, and
no profile or posting is read. Who counts is in queries/population.json and
what is counted in queries/measures.json. Every count of people passes the
small-cell rule; a series of dates merges neighbouring bands that would hold 1
to 9 people; and when the hidden cells of a published sum would add up to 1 to
9 people, one more cell is withheld. The run writes nothing until every count
is in, and stops without writing if a published cell could still be recovered.

Stage 2, the map, runs in the same pass: Meta's visible AI staff, the units
they name, and where the lab sits among them, as defined in
queries/mapping.json. It writes data/map_*.json.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import MIN_CELL, Platform, aggregate, write_json

POP = json.loads((HERE / "queries" / "population.json").read_text(encoding="utf-8"))
MEAS = json.loads((HERE / "queries" / "measures.json").read_text(encoding="utf-8"))
MAP = json.loads((HERE / "queries" / "mapping.json").read_text(encoding="utf-8"))
INST = json.loads(
    (HERE.parents[1] / MAP["china_educated"]["institutions_file"]).read_text(
        encoding="utf-8"
    )
)
SRC_POP = "queries/population.json"
SRC_BOTH = "queries/population.json · queries/measures.json"
SRC_MAP = "queries/population.json · queries/mapping.json"
MIN_BASE = 30  # a share is published only when its denominator is at least 30

CURRENT = {"field": "experience.is_current", "eq": True}
PAST = {"field": "experience.is_current", "eq": False}
# The intern rule, as two leaves in the entry's own all, so the tree stays shallow.
NOT_INTERN = [
    {"not": {"field": "experience.seniority", "eq": "Intern"}},
    {"not": {"field": "experience.title", "match": "intern"}},
]
DOCTORATE = {
    "has_education": {"all": [{"field": "education.degree", "eq": "Doctorate"}]}
}
US = {"field": "location.country", "eq": "United States"}


def text(terms: list[str]) -> dict:
    """Any term in the headline or the current title, matched word by word."""
    return {"any": [{"field": f, "match": t} for t in terms for f in POP["lab_fields"]]}


def entry(*conditions: dict) -> dict:
    """Conditions that must hold on one job entry."""
    return {"has_experience": {"all": list(conditions)}}


def at(names: list[str]) -> dict:
    return {"field": "experience.company.name", "in": names}


def started(op: str, date: str) -> dict:
    return {"field": "experience.start_date", op: date}


def ended_from(date: str) -> dict:
    return {"field": "experience.end_date", "gte": date}


class Lab:
    """A self-identified group: a current job at the employer and a lab term in the headline or title."""

    def __init__(
        self,
        employer: str,
        terms: list[str],
        history: list[str],
        cut: str,
        stay_end: str,
    ) -> None:
        self.employer = employer
        self.terms = terms
        self.history = history
        self.cut = cut
        self.stay_end = stay_end
        self.current = entry(
            {"field": "experience.company.name", "match": employer}, CURRENT
        )
        self.base = [self.current, text(terms)]

    def before(self, date: str, interns: bool = True) -> dict:
        """An entry at the employer that started before date; with interns=False, not an internship."""
        return entry(
            at(self.history), started("lt", date), *([] if interns else NOT_INTERN)
        )

    @property
    def stayed(self) -> dict:
        """A non-intern entry that began before the cut and was still running in stay_end or later."""
        return entry(
            at(self.history),
            started("lt", self.cut),
            *NOT_INTERN,
            {"any": [CURRENT, ended_from(self.stay_end)]},
        )

    @property
    def outside(self) -> list[dict]:
        """Everyone in the group who was not at the employer when the lab formed."""
        return [*self.base, {"not": self.stayed}]

    def n(self, p: Platform, *conditions: dict, base: list[dict] | None = None) -> int:
        return p.count(
            "people", {"all": (self.base if base is None else base) + list(conditions)}
        )


def share(part: object, whole: object) -> float | None:
    if isinstance(part, int) and isinstance(whole, int) and whole >= MIN_BASE:
        return round(part / whole, 4)
    return None


def small(v: object) -> bool:
    return isinstance(v, int) and 0 < v < MIN_CELL


def shown(v: int) -> int | str:
    return "<10" if small(v) else v


def protect(
    cells: dict[str, int], sums: list[list[str]]
) -> dict[str, int | str | None]:
    """What may be published of cells whose sums are published elsewhere.

    A cell of 1 to 9 is shown as "<10". When the hidden cells inside one published
    sum add up to 1 to 9, a reader could subtract their way to that group, so the
    smallest shown cell of 10 or more in the sum is withheld too (null).
    """
    hidden = {k for k, v in cells.items() if small(v)}
    withheld: set[str] = set()
    changed = True
    while changed:
        changed = False
        for members in sorted(sums, key=len):  # the narrowest sums first
            off = [k for k in members if k in hidden or k in withheld]
            if small(sum(cells[k] for k in off)):
                rest = [k for k in members if k not in off and cells[k] >= MIN_CELL]
                if not rest:
                    sys.exit(
                        f"Not written: the sum of {members} would give away a small group."
                    )
                withheld.add(min(rest, key=lambda k: cells[k]))
                changed = True
    return {
        k: None if k in withheld else "<10" if k in hidden else v
        for k, v in cells.items()
    }


GROUP = {
    "stayed": "stayed",
    "returned": "returned",
    "former_interns": "former-interns",
    "new": "new-to-employer",
    "earlier_not_stayed": "returned-or-former-interns",
    "outside": "outside-hires",
    "before": "earlier-job-at-employer",
}


def slug(value: str) -> str:
    return value.lower().replace("_", "-").replace(" ", "-")


def finest(splits: list[dict[str, int]], bad) -> dict[str, int] | None:
    """The first split, finest first, in which no cell is bad."""
    for cells in splits:
        if not any(bad(k, v) for k, v in cells.items()):
            return cells
    return None


def bands(
    edges: list[str], before: list[int], total: int, keep: set[str]
) -> list[tuple[str, int]]:
    """The edges left once no band between them holds 1 to 9 people.

    before[i] counts people before edges[i]. The first band runs from the start of
    the record, the last to the total. A band of 1 to 9 merges with its smaller
    neighbour, never across an edge in keep.
    """
    points = list(zip(edges, before))
    while True:
        cuts = [0] + [c for _, c in points] + [total]
        sizes = [b - a for a, b in pairwise(cuts)]
        if any(s < 0 for s in sizes):
            sys.exit(f"Not written: counts before {edges} do not rise with the date.")
        tiny = [i for i, s in enumerate(sizes) if small(s)]
        if not tiny:
            return points
        i = min(tiny, key=lambda j: sizes[j])
        options = []
        if i >= 1 and points[i - 1][0] not in keep:
            options.append((sizes[i - 1], i - 1))
        if i < len(points) and points[i][0] not in keep:
            options.append((sizes[i + 1], i))
        if not options:
            sys.exit(f"Not written: a band next to {sorted(keep)} holds 1 to 9 people.")
        del points[min(options)[1]]


def band_rows(
    points: list[tuple[str, int]], total: int, series: str, **extra: object
) -> list[dict]:
    rows, start, prev = [], None, 0
    for edge, c in [*points, (None, total)]:
        n = c - prev
        rows.append(
            {
                "series": series,
                "group": f"{start or ''}..{edge or ''}",
                "from": start,
                "before": edge,
                "count": shown(n),
                "share": share(n, total) if not small(n) else None,
                **extra,
            }
        )
        start, prev = edge, c
    return rows


def paired(a: list[tuple[str, int]], b: list[tuple[str, int]]) -> list[str]:
    """Edges kept in both series where the two cumulative counts differ by 1 to 9."""
    other = dict(b)
    return [e for e, c in a if e in other and small(c - other[e])]


def cohorts(p: Platform, lab: Lab) -> dict[str, int]:
    total = lab.n(p)
    before = lab.n(p, lab.before(lab.cut))
    before_job = lab.n(p, lab.before(lab.cut, interns=False))
    stayed = lab.n(p, lab.stayed)
    return {
        "total": total,
        "before": before,
        "before_job": before_job,
        "stayed": stayed,
        "returned": before_job - stayed,
        "former_interns": before - before_job,
        "new": total - before,
    }


# ---- Stage 2: the map ---------------------------------------------------------

BACHELOR = {"field": "education.degree", "eq": "Bachelor"}
ANY_BACHELOR = {"has_education": {"all": [BACHELOR]}}
# The China-educated study's mainland list: its match and exact names in one in
# leaf and its exclude words in another. On P2 this gives the same count as one
# match leaf per name, and it keeps every query under the limit of 64 conditions.
MAINLAND = {
    "has_education": {
        "all": [
            BACHELOR,
            {"field": "education.school.name", "in": INST["match"] + INST["exact"]},
            {"not": {"field": "education.school.name", "in": INST["exclude"]}},
        ]
    }
}
UNIT_ATTRS = [
    "research",
    "engineering",
    "manager_up",
    "doctorate",
    "us",
    "china_educated",
    "bachelor",
]


def words(
    terms: list[str], fields: tuple[str, ...] = ("headline", "current_title")
) -> dict:
    """Any of the terms in any of the fields, each term matched word by word."""
    return {"any": [{"field": f, "in": list(terms)} for f in fields]}


def fn_in(values: list[str]) -> dict:
    return {"field": "current_function", "in": values}


def level_in(values: list[str]) -> dict:
    return {"field": "current_seniority", "in": values}


def title_in(values: list[str], field: str = "current_title") -> dict:
    return {"field": field, "in": list(values)}


def map_count(p: Platform, meta: Lab) -> dict:
    """Every stage-2 count. Nothing here is published until map_tables has checked it."""
    pop = MAP["population"]
    lab_h, lab_t = (
        title_in(POP["lab_terms"], f) for f in ("headline", "current_title")
    )
    ai = {
        "any": [
            title_in(pop["ai_terms"], "headline"),
            title_in(pop["ai_terms"] + pop["title_only_terms"]),
        ]
    }
    big = entry(
        {"field": "experience.company.name", "match": POP["current_employer"]},
        CURRENT,
        {"field": "experience.company.size", "eq": pop["employer_size"]},
    )
    filters = (
        big,
        {"not": fn_in(pop["non_technical_functions"])},
        {"not": title_in(pop["non_technical_title_words"])},
    )
    # The lab passes every filter by construction, so the lab is the stage-1 group.
    p2 = [meta.current, ai, *({"any": [lab_h, lab_t, f]} for f in filters)]
    lab = meta.base
    groups = {"lab": lab, "p2": p2}

    def n(base: list[dict], *conditions: dict) -> int:
        return p.count("people", {"all": base + list(conditions)})

    out: dict = {}
    # 2. Size: current Meta profiles, split so that no count comes back banded.
    out["size"] = {
        "meta_us": n([meta.current], US),
        "big_us": n([big], US),
        "big_elsewhere": n([big], {"not": US}),
    }

    # 1. Units: the first unit in the fixed order whose terms a person names.
    attrs = {
        "research": fn_in(["Research"]),
        "engineering": fn_in(["Engineering and Technical"]),
        "manager_up": level_in(MEAS["roles"]["manager_up"]),
        "doctorate": DOCTORATE,
        "us": US,
        "china_educated": MAINLAND,
        "bachelor": ANY_BACHELOR,
    }
    units: dict[str, dict[str, int]] = {}
    earlier: list[str] = []
    for u in MAP["units"]["order"]:
        if u["id"] == "lab":
            # Count, function, doctorate, and US are the stage-1 counts of the same group.
            units["lab"] = {
                a: n(lab, attrs[a])
                for a in ("manager_up", "china_educated", "bachelor")
            }
        else:
            base = [*p2, words(u["terms"]), {"not": words(earlier)}]
            units[u["id"]] = {
                "count": n(base),
                **{a: n(base, c) for a, c in attrs.items()},
            }
        earlier += u["terms"]
    units["p2"] = {"count": n(p2), **{a: n(p2, c) for a, c in attrs.items()}}
    out["units"] = units

    # 3. Functions, beside research (a unit attribute): data titles, then the rest.
    fx = MAP["functions"]
    data_title = title_in(fx["data_title_words"])
    plain = {"not": data_title}
    out["functions"] = {
        g: {
            "data": n(b, {"not": fn_in(["Research"])}, data_title),
            "engineering": n(b, fn_in(["Engineering and Technical"]), plain),
            "product": n(b, fn_in(fx["product_functions"]), plain),
            "none": n(b, {"not": {"field": "current_function", "exists": True}}, plain),
        }
        for g, b in groups.items()
    }

    # 4. Levels; Vice President and above is manager_up minus the two levels below it.
    out["levels"] = {
        g: {
            lv["id"]: n(b, level_in(lv["values"]))
            for lv in MAP["levels"]["groups"]
            if lv["id"] != "vp-up"
        }
        for g, b in groups.items()
    }

    # 5. Titles that contain the words of each candidate.
    out["titles"] = {
        t: {g: n(b, {"field": "current_title", "match": t}) for g, b in groups.items()}
        for t in MAP["titles"]["candidates"]
    }

    # 6 and 9. Postings: Meta, the last 180 days, an AI title.
    po = MAP["postings"]
    jobs = [
        {"field": "company.name", "match": POP["current_employer"]},
        {"field": "posted_date", "gte": po["posted_from"]},
        title_in(pop["ai_terms"] + pop["title_only_terms"], "title"),
        {"not": title_in(pop["non_technical_title_words"], "title")},
    ]

    def jn(*conditions: dict) -> int:
        return p.count("jobs", {"all": jobs + list(conditions)})

    directions = {}
    for d in MAP["directions"]["list"]:
        stock = {
            "any": [
                title_in(d["phrase"], "headline"),
                title_in(d["phrase"]),
                title_in(d["word"], "skills"),
            ]
        }
        flow = {
            "any": [title_in(d["phrase"], "title"), title_in(d["word"], "description")]
        }
        directions[d["id"]] = {
            **{g: n(b, stock) for g, b in groups.items()},
            "postings": jn(flow),
        }
    out["directions"] = directions

    families: dict[str, int] = {"all": jn()}
    seen: list[str] = []
    for f in po["families"]:
        guard = [{"not": title_in(seen, "title")}] if seen else []
        families[f["id"]] = jn(title_in(f["title"], "title"), *guard)
        seen += f["title"]
    out["families"] = families

    pay_rule = MAP["pay"]
    paid = [
        {"field": "location.country", "eq": "United States"},
        {"field": "salary.currency", "eq": "USD"},
        {"field": "salary.annual_min", "exists": True},
        {"field": "salary.annual_max", "exists": True},
    ]
    pay: dict[str, dict] = {}
    seen = []
    for f in [{"id": "all", "title": []}, *po["families"][:3]]:
        cond = [*paid]
        if f["title"]:
            cond.append(title_in(f["title"], "title"))
        if seen:
            cond.append({"not": title_in(seen, "title")})
        row: dict = {"n": jn(*cond)}
        if row["n"] >= pay_rule["gate_count"]:
            for bound in ("annual_min", "annual_max"):
                row[bound] = {
                    t: jn(*cond, {"field": f"salary.{bound}", "gte": t})
                    for t in pay_rule[f"{bound}_thresholds"]
                }
        pay[f["id"]] = row
        seen += f["title"]
    out["pay"] = pay

    # 7. Sources: earlier employers, schools, and the China-educated split by level.
    src = MAP["sources"]
    reused = {r["id"] for r in MEAS["sources"]["context"]}
    out["employers"] = {
        e["id"]: {
            g: n(b, entry(at(e["names"]), PAST, *NOT_INTERN))
            for g, b in groups.items()
            if not (g == "lab" and e["id"] in reused)
        }
        for e in src["employers"]
    }
    out["schools"] = {
        s["id"]: {
            g: n(
                b,
                {
                    "has_education": {
                        "all": [title_in(s["names"], "education.school.name")]
                    }
                },
            )
            for g, b in groups.items()
        }
        for s in src["schools"]
    }
    ic = level_in(MAP["levels"]["individual_contributor"])
    mgr = level_in(MEAS["roles"]["manager_up"])
    out["china_levels"] = {
        g: {
            "china_educated_ic": n(b, MAINLAND, ic),
            "bachelor_ic": n(b, ANY_BACHELOR, ic),
            "china_educated_manager_up": n(b, MAINLAND, mgr),
            "bachelor_manager_up": n(b, ANY_BACHELOR, mgr),
        }
        for g, b in groups.items()
    }

    # 8. Flows since the cut, with the same window on both sides.
    fl = MAP["flows"]
    start = started("gte", fl["start_from"])
    end = ended_from(fl["ended_from"])
    history = POP["history_names"]
    # Meta is the same employer as in P2: the name with employer size 10,001+, since outside
    # the US the name alone also matches other companies. Facebook, Instagram, WhatsApp, and
    # Oculus keep their own company records, so they are matched by name.
    name = {"field": "experience.company.name", "match": POP["current_employer"]}
    sized = {"field": "experience.company.size", "eq": pop["employer_size"]}
    subsidiaries = [h for h in history if h != POP["current_employer"]]
    joined = entry(name, CURRENT, sized, start, *NOT_INTERN)
    left = {
        "any": [
            entry(name, sized, end, *NOT_INTERN),
            entry(at(subsidiaries), end, *NOT_INTERN),
        ]
    }
    rows = [{"id": "all", "where": [{"not": at(history)}]}] + [
        {
            "id": q["id"],
            "where": [at(q["names"])]
            + ([{"not": at(q["exclude"])}] if q.get("exclude") else []),
        }
        for q in fl["peers"]
    ]
    flows: dict[str, dict] = {}
    for r in rows:
        gone = [
            entry(*r["where"], CURRENT, start, *NOT_INTERN),
            left,
            # Anyone with a current entry under the name Meta, at any size, is not a leaver:
            # a current Meta job whose entry lacks a size must not count as a move away.
            {"not": meta.current},
        ]
        came = [joined, entry(*r["where"], end, *NOT_INTERN)]
        if r["id"] != "all":
            came.append({"not": entry(*r["where"], CURRENT)})
        for way, q in (("out", gone), ("in", came)):
            everyone = n(q)
            flows[f"{way} {r['id']}"] = {
                "all": everyone,
                "ai": n(q, ai) if everyone >= MIN_CELL else None,
            }
    out["flows"] = flows
    return out


class Book:
    """Every published stage-2 count, the sums a reader can form, and what stays hidden.

    cells are published counts; fixed ones were published in stage 1 and stay as
    they are. groups are counts a reader could work out but that are never
    published, such as a unit's staff outside the US. A sum says whole = parts.
    A count is known when it is published or when the sums, taken together,
    determine it (exact elimination over the unknown counts). resolve() withholds
    a count until no known count is a hidden cell or a group of 1 to 9 people, and
    no sum with a known whole leaves unknown parts that add up to 1 to 9; spare
    counts (the residual row) go first, then the smallest. Withheld counts that
    the sums determine anyway are published again, since hiding them hides nothing.
    """

    def __init__(self) -> None:
        self.value: dict[str, int] = {}
        self.fixed: set[str] = set()
        self.groups: set[str] = set()
        self.spare: set[str] = set()
        self.sums: list[tuple[str, list[str]]] = []
        self.withheld: set[str] = set()
        self.errors: list[str] = []

    def cell(self, key: str, value: int, published: object = True) -> str:
        """A count to publish; published is what stage 1 already shows, if anything."""
        self.value[key] = value
        if published is not True:
            if isinstance(published, int) and published == value:
                self.fixed.add(key)
            else:
                self.groups.add(key)  # stage 1 hid it, so no one knows it
        return key

    def group(self, key: str, value: int) -> str:
        self.value[key] = value
        self.groups.add(key)
        return key

    def total(self, whole: str, parts: list[str]) -> None:
        if sum(self.value[k] for k in parts) != self.value[whole]:
            self.errors.append(f"{whole} is not the sum of {parts}")
        self.sums.append((whole, parts))

    def contains(self, outer: str, inner: str) -> None:
        """inner is part of outer, so outer minus inner is a group too."""
        rest = self.group(
            f"{outer} minus {inner}", self.value[outer] - self.value[inner]
        )
        if self.value[rest] < 0:
            self.errors.append(f"{inner} is larger than {outer}")
        self.total(outer, [inner, rest])

    def visible(self, key: str) -> bool:
        return (
            key not in self.groups
            and key not in self.withheld
            and not small(self.value[key])
        )

    def known(self) -> set[str]:
        """Published counts and every unknown count the sums determine."""
        seen = {k for k in self.value if self.visible(k)}
        pivots: dict[str, dict[str, Fraction]] = {}
        for whole, parts in self.sums:
            row: dict[str, Fraction] = {}
            for k, sign in ((whole, 1), *((k, -1) for k in parts)):
                if k not in seen:
                    row[k] = row.get(k, Fraction(0)) + sign
            row = {k: v for k, v in row.items() if v}
            while hit := [k for k in row if k in pivots]:
                for k in hit:
                    factor = row.get(k)
                    if factor:
                        for c, v in pivots[k].items():
                            row[c] = row.get(c, Fraction(0)) - factor * v
                row = {k: v for k, v in row.items() if v}
            if not row:
                continue
            lead = min(row)
            row = {k: v / row[lead] for k, v in row.items()}
            for other in pivots.values():
                factor = other.get(lead)
                if factor:
                    for c, v in row.items():
                        other[c] = other.get(c, Fraction(0)) - factor * v
                    for c in [c for c, v in other.items() if not v]:
                        del other[c]
            pivots[lead] = row
        return seen | {k for k, row in pivots.items() if len(row) == 1}

    def leak(self, known: set[str]) -> list[str] | None:
        """The counts behind a small count or small group a reader could work out."""
        for k in known:
            if not self.visible(k) and small(self.value[k]):
                return [k]
        for whole, parts in self.sums:
            hidden = [k for k in parts if k not in known]
            if (
                whole in known
                and len(hidden) > 1
                and small(sum(self.value[k] for k in hidden))
            ):
                return hidden
        return None

    def movable(self, start: list[str]) -> str | None:
        """The published, movable count nearest the leak: spare ones first, then the smallest."""
        near: dict[str, list[int]] = {}
        for i, (whole, parts) in enumerate(self.sums):
            for k in (whole, *parts):
                near.setdefault(k, []).append(i)
        seen_cells, seen_sums, layer = set(start), set(), list(start)
        while layer:
            nxt: list[str] = []
            for k in layer:
                for i in near.get(k, []):
                    if i not in seen_sums:
                        seen_sums.add(i)
                        whole, parts = self.sums[i]
                        nxt += [c for c in (whole, *parts) if c not in seen_cells]
            seen_cells.update(nxt)
            options = [c for c in nxt if self.visible(c) and c not in self.fixed]
            if options:
                return min(
                    options, key=lambda c: (c not in self.spare, self.value[c], c)
                )
            layer = nxt
        return None

    def resolve(self) -> list[str]:
        while (bad := self.leak(self.known())) is not None:
            k = self.movable(bad)
            if k is None:
                return [*self.errors, f"{bad} could be worked out"]
            self.withheld.add(k)
        # A withheld count the sums determine anyway hides nothing: publish it.
        while back := self.withheld & self.known():
            self.withheld -= back
        if self.leak(self.known()) is not None:
            return [*self.errors, "publishing determined counts opened a leak"]
        return self.errors

    def show(self, key: str) -> int | str | None:
        if key in self.withheld or key in self.groups:
            return None
        return shown(self.value[key])


def map_tables(m: dict, s1: dict, snap: str) -> tuple[dict[str, dict], list[str]]:
    """Check every stage-2 count against the small-cell and recovery rules, then lay out the files.

    s1 holds stage-1 counts of the lab and what stage 1 published of them, since a
    stage-2 count that sits inside a stage-1 count forms a difference too.
    """
    book = Book()
    order = [u["id"] for u in MAP["units"]["order"]]
    ids = [*order, "none"]
    cols = ["count", *UNIT_ATTRS]
    units = {k: dict(v) for k, v in m["units"].items()}
    units["lab"].update(
        {
            c: s1["lab"][c][0]
            for c in ("count", "research", "engineering", "doctorate", "us")
        }
    )
    units["none"] = {c: units["p2"][c] - sum(units[u][c] for u in order) for c in cols}

    def uk(u: str, c: str) -> str:
        return f"unit {u} {c}"

    for u in [*ids, "p2"]:
        for c in cols:
            stage1 = s1["lab"].get(c) if u == "lab" else None
            book.cell(uk(u, c), units[u][c], stage1[1] if stage1 else True)
    book.spare.update(uk("none", c) for c in cols)
    for c in cols:
        book.total(uk("p2", c), [uk(u, c) for u in ids])
    for u in [*ids, "p2"]:
        for a in (
            "research",
            "engineering",
            "manager_up",
            "doctorate",
            "us",
            "bachelor",
        ):
            book.contains(uk(u, "count"), uk(u, a))
        book.contains(uk(u, "bachelor"), uk(u, "china_educated"))
        other = book.group(
            f"unit {u} other functions",
            units[u]["count"] - units[u]["research"] - units[u]["engineering"],
        )
        book.total(uk(u, "count"), [uk(u, "research"), uk(u, "engineering"), other])

    def s1cell(key: str) -> str:
        true, published = s1[key]
        return book.cell(f"stage 1 {key}", true, published)

    book.contains(s1cell("fair_only"), uk("fair", "count"))
    book.contains(uk("lab", "manager_up"), s1cell("research_manager_up"))

    # Size.
    sz = m["size"]
    for k, v in sz.items():
        book.cell(f"size {k}", v)
    book.contains("size meta_us", "size big_us")
    book.contains("size meta_us", uk("p2", "us"))

    # Functions: the lab and the rest of P2, each adding up to its total.
    rest_total = book.cell("rest count", units["p2"]["count"] - units["lab"]["count"])
    book.total(uk("p2", "count"), [uk("lab", "count"), rest_total])
    fn = {g: dict(v) for g, v in m["functions"].items()}
    for g in ("lab", "p2"):
        f = fn[g]
        f["research"] = units[g]["research"]
        f["other"] = units[g]["count"] - sum(
            f[k] for k in ("research", "data", "engineering", "product", "none")
        )
    fn["rest"] = {k: fn["p2"][k] - fn["lab"][k] for k in fn["p2"]}
    cats = ["research", "data", "engineering", "product", "other", "none"]
    # Stage 1 published the lab's functions without the data split; the pieces of
    # the data row that a reader could take from those cells are groups too.
    lab_e = fn["lab"]
    pieces = {
        "engineering": s1["engineering"][0] - lab_e["engineering"],
        "none": s1["not_stated"][0] - lab_e["none"],
        "other": s1["product"][0] + s1["other"][0] - lab_e["product"] - lab_e["other"],
    }
    merged = small(pieces["none"]) or small(pieces["other"])
    lab_cats = (
        ["research", "data", "engineering", "product", "other-or-none"]
        if merged
        else cats
    )
    if merged:
        lab_e["other-or-none"] = lab_e["other"] + lab_e["none"]
    fk = {
        g: {c: f"function {g} {c}" for c in (lab_cats if g == "lab" else cats)}
        for g in ("lab", "rest")
    }
    fk["lab"]["research"] = uk("lab", "research")
    for g in ("lab", "rest"):
        for c, key in fk[g].items():
            if key not in book.value:
                book.cell(key, fn[g][c])
    book.total(uk("p2", "research"), [uk("lab", "research"), fk["rest"]["research"]])
    book.total(uk("lab", "count"), list(fk["lab"].values()))
    book.total(rest_total, list(fk["rest"].values()))
    e_part = book.group("lab data titles in engineering", pieces["engineering"])
    book.total(s1cell("engineering"), [fk["lab"]["engineering"], e_part])
    s1_sum = book.group(
        "stage 1 lab product, other, and not stated",
        s1["product"][0] + s1["other"][0] + s1["not_stated"][0],
    )
    book.total(s1_sum, [s1cell("product"), s1cell("other"), s1cell("not_stated")])
    if merged:
        np_part = book.group(
            "lab data titles in other functions or none",
            pieces["none"] + pieces["other"],
        )
        book.total(s1_sum, [fk["lab"]["product"], fk["lab"]["other-or-none"], np_part])
        book.total(fk["lab"]["data"], [e_part, np_part])
    else:
        n_part = book.group("lab data titles with no function", pieces["none"])
        o_part = book.group("lab data titles in other functions", pieces["other"])
        book.total(s1cell("not_stated"), [fk["lab"]["none"], n_part])
        po_sum = book.group(
            "stage 1 lab product and other", s1["product"][0] + s1["other"][0]
        )
        book.total(po_sum, [s1cell("product"), s1cell("other")])
        book.total(po_sum, [fk["lab"]["product"], fk["lab"]["other"], o_part])
        book.total(fk["lab"]["data"], [e_part, n_part, o_part])
    rest_e = book.group(
        "rest engineering and technical",
        units["p2"]["engineering"] - units["lab"]["engineering"],
    )
    book.total(uk("p2", "engineering"), [uk("lab", "engineering"), rest_e])
    book.contains(rest_e, fk["rest"]["engineering"])

    # Levels, published as five groups: Intern joins Specialist (as in stage 1) and
    # Head, Director, and every level above them form one group, because the lab
    # holds fewer than 10 interns and fewer than 10 above Director.
    lv: dict[str, dict[str, int]] = {}
    for g in ("lab", "p2"):
        x = m["levels"][g]
        lv[g] = {
            "specialist-or-intern": x["intern"] + x["specialist"],
            "senior": x["senior"],
            "manager": x["manager"],
            "head-and-above": units[g]["manager_up"] - x["manager"],
            "none": units[g]["count"]
            - x["intern"]
            - x["specialist"]
            - x["senior"]
            - units[g]["manager_up"],
        }
    lv["rest"] = {k: lv["p2"][k] - lv["lab"][k] for k in lv["p2"]}
    lvl_ids = list(lv["p2"])
    lk = {
        g: {c: book.cell(f"level {g} {c}", lv[g][c]) for c in lvl_ids}
        for g in ("lab", "rest")
    }
    book.total(uk("lab", "count"), list(lk["lab"].values()))
    book.total(rest_total, list(lk["rest"].values()))
    top = ("manager", "head-and-above")
    book.total(uk("lab", "manager_up"), [lk["lab"][c] for c in top])
    book.total(uk("p2", "manager_up"), [lk[g][c] for g in ("lab", "rest") for c in top])
    book.contains(lk["lab"]["senior"], s1cell("research_senior"))
    book.contains(lk["lab"]["none"], s1cell("research_no_level"))
    book.contains(
        lk["lab"]["specialist-or-intern"], s1cell("research_specialist_or_intern")
    )

    # China-educated by level, only where every cell of a group holds 20 or more.
    cl = {g: dict(v) for g, v in m["china_levels"].items()}
    cl["rest"] = {k: cl["p2"][k] - cl["lab"][k] for k in cl["p2"]}
    gate = MAP["china_educated"]["level_gate_count"]
    china_groups = [g for g in ("lab", "rest") if min(cl[g].values()) >= gate]
    for g in china_groups:
        ck = {c: book.cell(f"china {g} {c}", v) for c, v in cl[g].items()}
        for lvl in ("ic", "manager_up"):
            book.contains(ck[f"bachelor_{lvl}"], ck[f"china_educated_{lvl}"])
        for c in ("china_educated", "bachelor"):
            whole = (
                uk("lab", c)
                if g == "lab"
                else book.group(f"rest {c}", units["p2"][c] - units["lab"][c])
            )
            if g == "rest":
                book.total(uk("p2", c), [uk("lab", c), whole])
            other_lv = book.group(
                f"china {g} {c} other levels",
                book.value[whole] - cl[g][f"{c}_ic"] - cl[g][f"{c}_manager_up"],
            )
            book.total(whole, [ck[f"{c}_ic"], ck[f"{c}_manager_up"], other_lv])

    # Titles, directions, employers, schools: rows that overlap, so no sums.
    titles = m["titles"]
    for t, v in titles.items():
        book.cell(f"title lab {t}", v["lab"])
        book.cell(f"title rest {t}", v["p2"] - v["lab"])
    dirs = m["directions"]
    for d, v in dirs.items():
        book.cell(f"direction lab {d}", v["lab"])
        book.cell(f"direction rest {d}", v["p2"] - v["lab"])
    for d, u in (
        ("ai-infrastructure", "infrastructure"),
        ("ranking-recommendations", "ranking"),
        ("ar-vr-devices", "reality-labs"),
    ):
        book.contains(f"direction rest {d}", uk(u, "count"))
    book.contains("direction lab ai-infrastructure", s1cell("team_infra"))
    emp = {}
    for e in MAP["sources"]["employers"]:
        v = m["employers"][e["id"]]
        lab_v = v["lab"] if "lab" in v else s1["context"][e["id"]][0]
        emp[e["id"]] = {"lab": lab_v, "rest": v["p2"] - lab_v}
        stage1 = s1["context"][e["id"]][1] if "lab" not in v else True
        book.cell(f"employer lab {e['id']}", lab_v, stage1)
        book.cell(f"employer rest {e['id']}", v["p2"] - lab_v)
    for s, v in m["schools"].items():
        book.cell(f"school lab {s}", v["lab"])
        book.cell(f"school rest {s}", v["p2"] - v["lab"])

    # A row that covers nearly all of the lab or the rest leaves a small remainder.
    for key in [
        k
        for k in book.value
        if k.startswith(("title ", "direction ", "employer ", "school "))
    ]:
        whole = uk("lab", "count") if key.split(" ")[1] == "lab" else rest_total
        book.contains(whole, key)

    # Flows.
    fl = m["flows"]
    for key, v in fl.items():
        book.cell(f"flow {key} all", v["all"])
        if v["ai"] is not None:
            book.cell(f"flow {key} ai", v["ai"])
            book.contains(f"flow {key} all", f"flow {key} ai")
    for key, v in fl.items():
        way, peer = key.split(" ", 1)
        if peer != "all":
            book.contains(f"flow {way} all all", f"flow {key} all")
            if v["ai"] is not None and fl[f"{way} all"]["ai"] is not None:
                book.contains(f"flow {way} all ai", f"flow {key} ai")

    problems = book.resolve()
    show = book.show
    files = map_files(
        m, snap, units, lab_cats, cats, lvl_ids, china_groups, show, merged
    )
    return files, problems


def map_files(
    m: dict,
    snap: str,
    units: dict,
    lab_cats: list[str],
    cats: list[str],
    lvl_ids: list[str],
    china_groups: list[str],
    show,
    merged: bool,
) -> dict[str, dict]:
    """The stage-2 aggregate files, from counts that map_tables has checked."""
    p2n, labn = units["p2"]["count"], units["lab"]["count"]
    restn = p2n - labn
    labels = {u["id"]: u["label"] for u in MAP["units"]["order"]} | {
        "none": MAP["units"]["none"]["label"]
    }

    def pair(g: str, key: str, base: int) -> dict:
        v = show(key)
        return {f"{g}_count": v, f"{g}_share": share(v, base)}

    size_rows = [
        {"group": "meta-current-us", "count": show("size meta_us"), "share": None},
        {"group": "meta-10001-us", "count": show("size big_us"), "share": None},
        {
            "group": "meta-10001-elsewhere-or-none",
            "count": show("size big_elsewhere"),
            "share": None,
        },
        {"group": "p2", "count": show("unit p2 count"), "share": None},
        {
            "group": "p2-us",
            "count": show("unit p2 us"),
            "share": share(show("unit p2 us"), p2n),
        },
        {
            "group": "lab",
            "count": show("unit lab count"),
            "share": share(show("unit lab count"), p2n),
        },
    ]
    unit_rows = []
    for u in [*[x["id"] for x in MAP["units"]["order"]], "none", "p2"]:
        cnt = show(f"unit {u} count")
        row = {
            "group": u,
            "label": labels.get(u, "Meta's visible AI staff (P2)"),
            "count": cnt,
            "share": share(cnt, p2n) if u != "p2" else None,
        }
        for a in UNIT_ATTRS:
            v = show(f"unit {u} {a}")
            base = show(f"unit {u} bachelor") if a == "china_educated" else cnt
            row[f"{a}_count"] = v
            row[f"{a}_share"] = share(v, base) if a != "bachelor" else share(v, cnt)
        unit_rows.append(row)

    fn_rows = []
    for c in dict.fromkeys([*cats, *lab_cats]):
        row = {"group": c}
        if c in lab_cats:
            key = "unit lab research" if c == "research" else f"function lab {c}"
            row |= pair("lab", key, labn)
        else:
            row |= {"lab_count": None, "lab_share": None}
        if c in cats:
            row |= pair("rest", f"function rest {c}", restn)
        else:
            parts = [show(f"function rest {x}") for x in ("other", "none")]
            v = sum(parts) if all(isinstance(x, int) for x in parts) else None
            row |= {"rest_count": v, "rest_share": share(v, restn)}
        fn_rows.append(row)
    level_rows = [
        {
            "group": c,
            **pair("lab", f"level lab {c}", labn),
            **pair("rest", f"level rest {c}", restn),
        }
        for c in lvl_ids
    ]
    ranked = sorted(m["titles"], key=lambda t: (-m["titles"][t]["p2"], t))[
        : MAP["titles"]["publish"]
    ]
    title_rows = [
        {
            "group": slug(t),
            "label": t,
            **pair("lab", f"title lab {t}", labn),
            **pair("rest", f"title rest {t}", restn),
        }
        for t in ranked
    ]
    dir_labels = {d["id"]: d["label"] for d in MAP["directions"]["list"]}
    dir_rows = [
        {
            "group": d,
            "label": dir_labels[d],
            **pair("lab", f"direction lab {d}", labn),
            **pair("rest", f"direction rest {d}", restn),
        }
        for d in m["directions"]
    ]
    src_rows = [
        {
            "set": "ever-worked-at",
            "group": e["id"],
            "label": e["label"],
            **pair("lab", f"employer lab {e['id']}", labn),
            **pair("rest", f"employer rest {e['id']}", restn),
        }
        for e in MAP["sources"]["employers"]
    ]
    src_rows += [
        {
            "set": "school",
            "group": s["id"],
            "label": s["label"],
            **pair("lab", f"school lab {s['id']}", labn),
            **pair("rest", f"school rest {s['id']}", restn),
        }
        for s in MAP["sources"]["schools"]
    ]
    lab_c, lab_b = show("unit lab china_educated"), show("unit lab bachelor")
    rest_c = units["p2"]["china_educated"] - units["lab"]["china_educated"]
    rest_b = units["p2"]["bachelor"] - units["lab"]["bachelor"]
    src_rows.append(
        {
            "set": "china-educated",
            "group": "all-levels",
            "label": "Bachelor's at a mainland-China institution, of those with a Bachelor entry",
            "lab_count": lab_c,
            "lab_base_count": lab_b,
            "lab_share": share(lab_c, lab_b),
            "rest_count": shown(rest_c),
            "rest_base_count": shown(rest_b),
            "rest_share": share(shown(rest_c), shown(rest_b)),
        }
    )
    for lvl, label in (
        ("ic", "Individual contributors (Intern, Specialist, Senior)"),
        ("manager_up", "Manager and above"),
    ):
        row = {
            "set": "china-educated-by-level",
            "group": lvl.replace("_", "-"),
            "label": label,
        }
        for g in ("lab", "rest"):
            if g in china_groups:
                c, b = (
                    show(f"china {g} china_educated_{lvl}"),
                    show(f"china {g} bachelor_{lvl}"),
                )
                row |= {
                    f"{g}_count": c,
                    f"{g}_base_count": b,
                    f"{g}_share": share(c, b),
                }
            else:
                row |= {f"{g}_count": None, f"{g}_base_count": None, f"{g}_share": None}
        src_rows.append(row)

    peer_labels = {"all": "Any employer outside Meta"} | {
        q["id"]: q["label"] for q in MAP["flows"]["peers"]
    }
    flow_rows = []
    for key, v in m["flows"].items():
        way, peer = key.split(" ", 1)
        cnt = show(f"flow {key} all")
        ai_v = show(f"flow {key} ai") if v["ai"] is not None else None
        flow_rows.append(
            {
                "direction": way,
                "group": peer,
                "label": peer_labels[peer],
                "count": cnt,
                "ai_titled_count": ai_v,
                "ai_titled_share": share(ai_v, cnt),
            }
        )

    fam = m["families"]
    fam_labels = {f["id"]: f["label"] for f in MAP["postings"]["families"]}
    other_fam = fam["all"] - sum(fam[f] for f in fam_labels)
    posting_rows = [
        {
            "set": "family",
            "group": f,
            "label": fam_labels[f],
            "count": fam[f],
            "share": share(fam[f], fam["all"]),
        }
        for f in fam_labels
    ] + [
        {
            "set": "family",
            "group": "other",
            "label": "Other titles",
            "count": other_fam,
            "share": share(other_fam, fam["all"]),
        }
    ]
    posting_rows += [
        {
            "set": "direction",
            "group": d,
            "label": dir_labels[d],
            "count": v["postings"],
            "share": share(v["postings"], fam["all"]),
        }
        for d, v in m["directions"].items()
    ]
    pay_rows = []
    for f, v in m["pay"].items():
        label = "All AI postings" if f == "all" else fam_labels[f]
        published = v["n"] >= MAP["pay"]["gate_count"]
        pay_rows.append(
            {
                "family": f,
                "label": label,
                "bound": None,
                "at_least": None,
                "count": v["n"],
                "share": None,
                "published": published,
            }
        )
        if published:
            for bound in ("annual_min", "annual_max"):
                for t, c in v[bound].items():
                    pay_rows.append(
                        {
                            "family": f,
                            "label": label,
                            "bound": bound,
                            "at_least": t,
                            "count": c,
                            "share": share(c, v["n"]),
                            "published": True,
                        }
                    )

    return {
        "map_size.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            size_rows,
            note=(
                "meta-current-us: current Meta entries (the name Meta, which outside the US also matches other "
                "companies, so no global count is given). meta-10001: current Meta entries whose employer size is "
                "10,001+, in the US and elsewhere or with no country. p2: Meta's visible AI staff (queries/mapping.json). "
                "Visible profiles include contractors and people who left without updating their profile; compare them "
                "with the company's reported headcount only as a coverage ratio."
            ),
        ),
        "map_units.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            unit_rows,
            p2_count=show("unit p2 count"),
            note=(
                "Each person counts at the first unit in the order of queries/mapping.json whose terms appear in the "
                "headline or current title; the rows add up to the p2 row. Shares of a unit are of its count, except "
                "china_educated_share, which is of bachelor_count. The lab row is the stage-1 group. Null means withheld "
                "so that no group of 1 to 9 people can be worked out."
            ),
        ),
        "map_functions.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            fn_rows,
            lab_count=show("unit lab count"),
            rest_count=show("rest count"),
            lab_other_and_none_merged=merged,
            note=(
                "Exclusive, in order: research (current_function Research), data (a data title, not research), "
                "engineering (Engineering and Technical), product (Product, Design, Project Management), other stated, "
                "none stated. rest is P2 without the lab. When lab_other_and_none_merged is true, the lab's other and "
                "none are one row, other-or-none, because stage 1 published the lab's functions and a separate row "
                "would let a reader work out fewer than 10 people."
            ),
        ),
        "map_levels.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            level_rows,
            lab_count=show("unit lab count"),
            rest_count=show("rest count"),
            note=(
                "current_seniority in five groups: specialist-or-intern (Intern and Specialist), senior, manager, "
                "head-and-above (Head, Director, Vice President, President/Vice President, C-Level, Partner, "
                "Founder, Owner), and none stated. Intern and the levels above Director are merged into their "
                "neighbours because the lab holds fewer than 10 of each. A visible hierarchy, not a reporting line."
            ),
        ),
        "map_titles.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            title_rows,
            lab_count=show("unit lab count"),
            rest_count=show("rest count"),
            note="Current titles that contain all the words of the label, in any order; rows overlap. The ten candidates with the most P2 profiles.",
        ),
        "map_directions.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            dir_rows,
            lab_count=show("unit lab count"),
            rest_count=show("rest count"),
            note="Stock: profiles whose headline or current title names the direction, or whose skills list one of its words; a person can count in several.",
        ),
        "map_sources.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            src_rows,
            lab_count=show("unit lab count"),
            rest_count=show("rest count"),
            note=(
                "ever-worked-at: a past non-intern job at the employer, any time; the lab's first six rows equal "
                "data/sources.json. school: any education entry there. china-educated: a Bachelor entry at a mainland-"
                "China institution (the China-educated study's list), of those with a Bachelor entry; by level only where "
                "all four cells of a group hold 20 or more. Rows overlap."
            ),
        ),
        "map_flows.json": aggregate(
            "profiles",
            snap,
            SRC_MAP,
            flow_rows,
            start_from=MAP["flows"]["start_from"],
            ended_from=MAP["flows"]["ended_from"],
            note=(
                "out: a current non-intern job at the employer that started on or after start_from, a non-intern Meta "
                "job that ended on or after ended_from, and no current Meta job. in: a current non-intern Meta job that "
                "started on or after start_from and a non-intern job at the employer that ended on or after ended_from, "
                "and no current job there. all: any employer outside Meta. ai_titled_count: the P2 AI terms in the "
                "headline or current title, counted where the row holds 10 or more. Profiles lag: dates stop in April "
                "2026. Rows can overlap."
            ),
        ),
        "map_postings.json": aggregate(
            "jobs",
            snap,
            SRC_MAP,
            posting_rows,
            all_count=fam["all"],
            note=(
                "Meta postings posted in the last 180 days with an AI title (queries/mapping.json), open on the day. "
                "family: exclusive, first match in order. direction: title or description names it; rows overlap. "
                "A role posted in several cities counts once per city."
            ),
        ),
        "map_pay.json": aggregate(
            "jobs",
            snap,
            SRC_MAP,
            pay_rows,
            gate_count=MAP["pay"]["gate_count"],
            note=(
                "US postings in USD that state both annual_min and annual_max: count is how many do, and each threshold "
                "row how many state a bound at or above at_least. Posted base ranges only, not pay, bonus, or equity. A "
                "family is published only with gate_count or more such postings."
            ),
        ),
    }


def main() -> int:
    p = Platform(max_credits=400)
    snap = p.snapshot
    family = POP["history_names"]
    meta = Lab(
        POP["current_employer"], POP["lab_terms"], family, POP["cut"], POP["stay_end"]
    )
    narrow = Lab(
        POP["current_employer"],
        POP["narrow_terms"],
        family,
        POP["cut"],
        POP["stay_end"],
    )
    cmp_ = POP["comparison"]
    msft = Lab(
        cmp_["current_employer"],
        cmp_["lab_terms"],
        cmp_["history_names"],
        cmp_["cut"],
        cmp_["stay_end"],
    )

    # 1. Cohorts: stayed, returned, former interns, new to the employer.
    c = cohorts(p, meta)
    total = c["total"]
    outside = total - c["stayed"]
    nc = {
        "total": narrow.n(p),
        "before": narrow.n(p, narrow.before(narrow.cut)),
        "stayed": narrow.n(p, narrow.stayed),
    }
    mc = cohorts(p, msft)
    labeling = meta.n(p, text(POP["labeling_terms"]), base=meta.outside)

    # 2. First Meta job: every entry, then non-intern entries only; and Microsoft.
    fj = MEAS["first_joined"]
    pre = fj["edges"]
    post = fj["after_cut_edges"]
    first_all = (
        [meta.n(p, meta.before(e)) for e in pre]
        + [c["before"]]
        + [meta.n(p, meta.before(e)) for e in post]
    )
    first_job = [meta.n(p, meta.before(e, interns=False)) for e in pre] + [
        c["before_job"]
    ]
    ms_first = [msft.n(p, msft.before(e)) for e in cmp_["edges"]] + [mc["before"]]

    # 3. For those who stayed: when their newest current Meta entry started.
    mv = MEAS["moves"]["edges"]
    since = [
        meta.n(p, meta.stayed, entry(at(family), CURRENT, started("gte", e)))
        for e in mv
    ]

    # 4. Where the outside hires had just been: disjoint rows in a fixed order.
    src = MEAS["sources"]
    window = ended_from(src["ended_from"])
    source_cells: dict[str, int] = {}
    earlier: list[str] = []
    for row in src["order"]:
        if "names" in row:
            hit = entry(at(row["names"]), window, *NOT_INTERN)
        else:
            hit = entry(
                {"field": "experience.company.type", "eq": row["company_type"]}, window
            )
        guard = [{"not": entry(at(earlier), window, *NOT_INTERN)}] if earlier else []
        source_cells[row["id"]] = meta.n(p, hit, *guard, base=meta.outside)
        earlier += row.get("names", [])
    context_cells = {
        row["id"]: meta.n(p, entry(at(row["names"]), PAST, *NOT_INTERN))
        for row in src["context"]
    }

    # 5. Roles: function by cohort; level and doctorates against Meta's other research staff.
    roles = MEAS["roles"]
    fn_all = {
        f: meta.n(p, {"field": "current_function", "eq": f}) for f in roles["functions"]
    }
    fn_all["stated"] = meta.n(p, {"field": "current_function", "exists": True})
    fn_out = {
        f: meta.n(p, {"field": "current_function", "eq": f}, base=meta.outside)
        for f in roles["functions"]
    }
    fn_out["stated"] = meta.n(
        p, {"field": "current_function", "exists": True}, base=meta.outside
    )
    research = {"field": "current_function", "eq": "Research"}
    lab_research = [*meta.base, research]
    baseline = [meta.current, research, {"not": text(POP["lab_terms"])}]

    def levels(base: list[dict]) -> dict[str, int]:
        return {
            "senior": meta.n(
                p, {"field": "current_seniority", "in": roles["senior"]}, base=base
            ),
            "manager_up": meta.n(
                p, {"field": "current_seniority", "in": roles["manager_up"]}, base=base
            ),
            "stated": meta.n(
                p, {"field": "current_seniority", "exists": True}, base=base
            ),
        }

    lv_lab = {"total": fn_all["Research"], **levels(lab_research)}
    lv_base = {"total": meta.n(p, base=baseline), **levels(baseline)}
    doc = {
        "all": meta.n(p, DOCTORATE),
        "outside": meta.n(p, DOCTORATE, base=meta.outside),
        "lab_research": meta.n(p, DOCTORATE, base=lab_research),
        "baseline": meta.n(p, DOCTORATE, base=baseline),
    }

    # 6. Sub-teams named in the headline or title, and FAIR outside the population.
    teams = {t["id"]: meta.n(p, text(t["terms"])) for t in MEAS["teams"]}
    fair_only = meta.n(
        p, base=[meta.current, text(["FAIR"]), {"not": text(POP["lab_terms"])}]
    )

    # 7. Where people list themselves.
    pl = MEAS["places"]
    us = meta.n(p, US)
    states = {
        s: meta.n(p, US, {"field": "location.state", "eq": s}) for s in pl["states"]
    }
    bay = meta.n(
        p,
        US,
        {"field": "location.state", "eq": "California"},
        {"field": "location.city", "in": pl["bay_area"]},
    )
    countries = {
        k: meta.n(p, {"field": "location.country", "eq": k}) for k in pl["countries"]
    }

    # 8. Open postings that name the lab.
    po = MEAS["postings"]
    j_base = [
        {"field": "company.name", "match": po["company"]},
        {"field": "is_open", "eq": True},
        {
            "any": [{"field": "title", "match": t} for t in po["title_terms"]]
            + [{"field": "description", "match": t} for t in po["description_terms"]]
        },
    ]

    def jobs(*conditions: dict) -> int:
        return p.count("jobs", {"all": j_base + list(conditions)})

    jc = {
        "all": jobs(),
        "research": jobs({"field": "title", "match": po["research_title"]}),
        **{
            f"city:{k}": jobs({"field": "location.city", "eq": k}) for k in po["cities"]
        },
        **{
            f"state:{k}": jobs({"field": "location.state", "eq": k})
            for k in po["states"]
        },
        "stated": jobs({"field": "min_experience_months", "exists": True}),
        "le_max": jobs(
            {"field": "min_experience_months", "lte": po["experience_max_months"]}
        ),
        "not_applicable": jobs({"field": "seniority", "eq": "Not Applicable"}),
        "posted_recent": jobs({"field": "posted_date", "gte": po["posted_from"]}),
    }
    meta_open = p.count(
        "jobs",
        {
            "all": [
                {"field": "company.name", "match": po["company"]},
                {"field": "is_open", "eq": True},
            ]
        },
    )

    # Stage 2, the map, in the same run.
    m2 = map_count(p, meta)

    # ---- Everything is counted; nothing below calls the Platform. ----

    problems = []

    # Cohorts, as one partition of the total for each lab.
    cells = {k: c[k] for k in ("stayed", "returned", "former_interns", "new")}
    # The first-job series publish the counts before the cut too, so the groups that
    # had a Meta job before it (with or without internships) are published sums.
    pub = protect(
        cells,
        [list(cells), ["stayed", "returned"], ["stayed", "returned", "former_interns"]],
    )
    # The narrow group sits inside the main one, so the difference between two
    # matching cells is a group too. It is split as finely as that allows.
    main_of = {
        "stayed": c["stayed"],
        "earlier_not_stayed": c["returned"] + c["former_interns"],
        "new": c["new"],
        "outside": outside,
    }
    n_cells = finest(
        [
            {
                "stayed": nc["stayed"],
                "earlier_not_stayed": nc["before"] - nc["stayed"],
                "new": nc["total"] - nc["before"],
            },
            {"stayed": nc["stayed"], "outside": nc["total"] - nc["stayed"]},
        ],
        lambda k, v: small(v) or small(main_of[k] - v),
    )
    if n_cells is None or small(total - nc["total"]):
        problems.append("superintelligence-only: no split keeps every difference")
    # Microsoft: the four groups when none is small; otherwise an earlier job there
    # and new, the split its first-job series shows anyway.
    ms_cells = finest(
        [
            {k: mc[k] for k in ("stayed", "returned", "former_interns", "new")},
            {"before": mc["before"], "new": mc["new"]},
        ],
        lambda k, v: small(v),
    )
    if ms_cells is None:
        problems.append("microsoft: no split without a small group")

    cohort_rows = [
        {
            "lab": "meta",
            "definition": "superintelligence-or-msl",
            "group": GROUP[k],
            "count": v,
            "share": share(v, total),
        }
        for k, v in pub.items()
    ]
    cohort_rows += [
        {
            "lab": "meta",
            "definition": "superintelligence-only",
            "group": GROUP[k],
            "count": v,
            "share": share(v, nc["total"]),
        }
        for k, v in (n_cells or {}).items()
    ]
    cohort_rows += [
        {
            "lab": "microsoft",
            "definition": "superintelligence",
            "group": GROUP[k],
            "count": v,
            "share": share(v, mc["total"]),
        }
        for k, v in (ms_cells or {}).items()
    ]

    # First Meta job, as bands; the non-intern series may keep only edges whose
    # difference from the every-entry series is 0 or at least 10.
    edges_all = pre + [POP["cut"]] + post
    keep = {POP["cut"]}
    pts_all = bands(edges_all, first_all, total, keep)
    job_edges = pre + [POP["cut"]]
    pts_job = bands(job_edges, first_job, total, keep)
    while bad := [e for e in paired(pts_all, pts_job) if e not in keep]:
        pts_job = bands(
            [e for e, _ in pts_job if e not in bad],
            [v for e, v in pts_job if e not in bad],
            total,
            keep,
        )
    if paired(pts_all, pts_job):
        problems.append("first Meta job: the two series differ by 1 to 9 at the cut")
    pts_ms = bands(cmp_["edges"] + [cmp_["cut"]], ms_first, mc["total"], {cmp_["cut"]})
    first_rows = (
        band_rows(pts_all, total, "meta-any-entry")
        + band_rows(pts_job, total, "meta-first-non-intern-job")
        + band_rows(pts_ms, mc["total"], "microsoft-any-entry")
    )

    # When those who stayed started their newest current role, and when the new joined.
    pts_mv = bands(mv, [c["stayed"] - s for s in since], c["stayed"], {POP["cut"]})
    move_rows = band_rows(pts_mv, c["stayed"], "stayed-newest-current-role")
    new_pts = [(e, v - c["before"]) for e, v in pts_all if e in post]
    move_rows += band_rows(
        [(POP["cut"], 0), *new_pts], c["new"], "new-to-meta-first-job"
    )[1:]

    # Sources: one partition of the outside hires, and the AI-lab subtotal.
    source_cells["other"] = outside - sum(source_cells.values())
    ai = [r["id"] for r in src["order"] if r.get("ai_lab")]
    ai_total = sum(source_cells[k] for k in ai)
    # The AI-lab subtotal is published only when it is not itself a small group.
    s_pub = protect(
        source_cells, [list(source_cells)] + ([ai] if not small(ai_total) else [])
    )
    labels = {r["id"]: r["label"] for r in src["order"]} | {
        "other": "Other employers, or none that ended in 2025 or later"
    }
    source_rows = [
        {
            "set": "came-from",
            "group": k,
            "label": labels[k],
            "ai_lab": k in ai,
            "count": v,
            "share": share(v, outside),
        }
        for k, v in s_pub.items()
    ]
    ctx_labels = {r["id"]: r["label"] for r in src["context"]}
    source_rows += [
        {
            "set": "ever-worked-at",
            "group": k,
            "label": ctx_labels[k],
            "count": shown(v),
            "share": share(shown(v), total),
        }
        for k, v in context_cells.items()
    ]

    # Functions: rows add up to each cohort, and the two cohorts add up to the group.
    fkeys = roles["functions"]

    def fn_cells(d: dict[str, int], whole: int) -> dict[str, int]:
        out = {f: d[f] for f in fkeys}
        out["other"] = d["stated"] - sum(d[f] for f in fkeys)
        out["not_stated"] = whole - d["stated"]
        return out

    fa, fo = fn_cells(fn_all, total), fn_cells(fn_out, outside)
    fs = {k: fa[k] - fo[k] for k in fa}
    grid = (
        {f"all:{k}": v for k, v in fa.items()}
        | {f"out:{k}": v for k, v in fo.items()}
        | {f"stay:{k}": v for k, v in fs.items()}
    )
    sums = [[f"{col}:{k}" for k in fa] for col in ("all", "out", "stay")] + [
        [f"out:{k}", f"stay:{k}"] for k in fa
    ]
    g = protect(grid, sums)
    role_rows = [
        {
            "table": "function",
            "group": slug(k),
            "count": g[f"all:{k}"],
            "share": share(g[f"all:{k}"], total),
            "stayed_count": g[f"stay:{k}"],
            "stayed_share": share(g[f"stay:{k}"], c["stayed"]),
            "outside_count": g[f"out:{k}"],
            "outside_share": share(g[f"out:{k}"], outside),
        }
        for k in fa
    ]

    def lv_cells(d: dict[str, int]) -> dict[str, int]:
        return {
            "senior": d["senior"],
            "manager_up": d["manager_up"],
            "specialist_or_intern": d["stated"] - d["senior"] - d["manager_up"],
            "not_stated": d["total"] - d["stated"],
        }

    la, lb = lv_cells(lv_lab), lv_cells(lv_base)
    pa, pb = protect(la, [list(la)]), protect(lb, [list(lb)])
    role_rows += [
        {
            "table": "level-in-research",
            "group": slug(k),
            "lab_count": pa[k],
            "lab_share": share(pa[k], lv_lab["total"]),
            "baseline_count": pb[k],
            "baseline_share": share(pb[k], lv_base["total"]),
        }
        for k in la
    ]
    d_cells = {"outside": doc["outside"], "stayed": doc["all"] - doc["outside"]}
    d_pub = protect(d_cells, [list(d_cells)])
    for group, n, base in (
        ("all", shown(doc["all"]), total),
        ("stayed", d_pub["stayed"], c["stayed"]),
        ("outside", d_pub["outside"], outside),
        ("lab-research", shown(doc["lab_research"]), lv_lab["total"]),
        ("baseline-research", shown(doc["baseline"]), lv_base["total"]),
    ):
        role_rows.append(
            {
                "table": "doctorate",
                "group": group,
                "count": n,
                "base_count": base,
                "share": share(n, base),
            }
        )

    # Sub-teams overlap and have no total; each row stands alone.
    team_rows = [
        {
            "group": t["id"],
            "label": t["label"],
            "count": shown(teams[t["id"]]),
            "share": share(shown(teams[t["id"]]), total),
        }
        for t in MEAS["teams"]
    ]
    team_rows.append(
        {
            "group": "fair-only",
            "label": "Current Meta profiles naming FAIR and no lab term (outside the population)",
            "count": shown(fair_only),
            "share": None,
        }
    )

    # Places: one partition of the group, the US inside it, and the Bay Area inside California.
    place_cells = {
        "bay-area": bay,
        "california-other": states["California"] - bay,
        **{
            s.lower().replace(" ", "-"): v
            for s, v in states.items()
            if s != "California"
        },
        "us-other": us - sum(states.values()),
        **{k.lower().replace(" ", "-"): v for k, v in countries.items()},
        "elsewhere-or-none": total - us - sum(countries.values()),
    }
    us_keys = ["bay-area", "california-other", "new-york", "washington", "us-other"]
    pp = protect(
        place_cells, [list(place_cells), us_keys, ["bay-area", "california-other"]]
    )
    place_rows = [
        {"group": k, "count": v, "share": share(v, total)} for k, v in pp.items()
    ]

    # Postings: not people, so no minimum.
    j_all = jc["all"]
    placed = sum(v for k, v in jc.items() if k.startswith(("city:", "state:")))
    posting_rows = [
        {"group": "all", "count": j_all, "share": share(j_all, j_all)},
        {
            "group": "research-titles",
            "count": jc["research"],
            "share": share(jc["research"], j_all),
        },
        *[
            {
                "group": k.split(":", 1)[1].lower().replace(" ", "-"),
                "count": v,
                "share": share(v, j_all),
            }
            for k, v in jc.items()
            if k.startswith(("city:", "state:"))
        ],
        {
            "group": "other-locations",
            "count": j_all - placed,
            "share": share(j_all - placed, j_all),
        },
        {
            "group": "experience-stated",
            "count": jc["stated"],
            "share": share(jc["stated"], j_all),
        },
        {
            "group": f"experience-{po['experience_max_months']}-months-or-less",
            "count": jc["le_max"],
            "share": share(jc["le_max"], jc["stated"]),
        },
        {
            "group": "seniority-not-applicable",
            "count": jc["not_applicable"],
            "share": share(jc["not_applicable"], j_all),
        },
        {
            "group": f"posted-since-{po['posted_from']}",
            "count": jc["posted_recent"],
            "share": share(jc["posted_recent"], j_all),
        },
    ]

    # Stage 2 is checked against what stage 1 publishes of the same lab.
    s1 = {
        "lab": {
            "count": (total, total),
            "research": (fa["Research"], g["all:Research"]),
            "engineering": (
                fa["Engineering and Technical"],
                g["all:Engineering and Technical"],
            ),
            "doctorate": (doc["all"], shown(doc["all"])),
            "us": (us, us),
        },
        "engineering": (
            fa["Engineering and Technical"],
            g["all:Engineering and Technical"],
        ),
        "product": (fa["Product"], g["all:Product"]),
        "other": (fa["other"], g["all:other"]),
        "not_stated": (fa["not_stated"], g["all:not_stated"]),
        "research_senior": (la["senior"], pa["senior"]),
        "research_manager_up": (la["manager_up"], pa["manager_up"]),
        "research_specialist_or_intern": (
            la["specialist_or_intern"],
            pa["specialist_or_intern"],
        ),
        "research_no_level": (la["not_stated"], pa["not_stated"]),
        "fair_only": (fair_only, shown(fair_only)),
        "team_infra": (teams["infra"], shown(teams["infra"])),
        "context": {k: (v, shown(v)) for k, v in context_cells.items()},
    }
    map_out, map_problems = map_tables(m2, s1, snap)
    problems += [f"map: {x}" for x in map_problems]

    if problems:
        sys.exit(
            "Not written; these cells could be recovered:\n  " + "\n  ".join(problems)
        )

    # ---- Write only now, so a stopped run leaves data/ as it was. ----
    write_json(
        HERE,
        "cohorts.json",
        aggregate(
            "profiles",
            snap,
            SRC_POP,
            cohort_rows,
            meta_total_count=total,
            meta_outside_count=outside,
            meta_outside_share=share(outside, total),
            meta_outside_labeling_count=shown(labeling),
            meta_superintelligence_only_total_count=nc["total"],
            microsoft_total_count=mc["total"],
            cut=POP["cut"],
            microsoft_cut=cmp_["cut"],
            note=(
                "The groups of each lab add up to its total. Meta, main definition: stayed (a "
                "non-intern job at Meta that began before the cut and ran into May 2025 or "
                "later), returned (an earlier non-intern Meta job, but not at Meta then), "
                "former interns (only internships there before the cut), and new to the "
                "employer. Outside hires are everyone who did not stay. The narrow "
                "definition and Microsoft are split as finely as the small-cell rule allows: "
                "a difference between a narrow cell and the matching main cell is a group too. "
                "earlier-job-at-employer is anyone with an entry there that began before the "
                "cut. meta_outside_labeling_count counts outside hires whose title or "
                "headline names data labeling, annotation, or red teaming."
            ),
        ),
    )
    write_json(
        HERE,
        "first_joined.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            first_rows,
            meta_total_count=total,
            microsoft_total_count=mc["total"],
            cut=POP["cut"],
            microsoft_cut=cmp_["cut"],
            note=(
                "Bands of the date each person's first job at the employer started, from counts of people with an "
                "entry there that started before each date; from is the first day of the band and before the day "
                "after it ends, null at the open ends. meta-first-non-intern-job skips internships and runs to the "
                "cut; its last band is everyone without a non-intern Meta job before the cut. Bands that would hold "
                "1 to 9 people are merged with a neighbour. The last Meta band includes the fewer than 10 whose "
                "Meta entry has no start date. Profiles lag: start dates stop in April 2026."
            ),
        ),
    )
    write_json(
        HERE,
        "moves.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            move_rows,
            stayed_count=c["stayed"],
            new_count=c["new"],
            note=(
                "stayed-newest-current-role: people who were at Meta when the lab formed, by the month their newest "
                "current Meta entry started; the first band also holds entries with no start date. "
                "new-to-meta-first-job: people new to Meta, by the month their first Meta entry started; the last "
                "band includes the fewer than 10 with no start date. Many people change teams without a new entry, "
                "so a new entry is a lower bound on who moved."
            ),
        ),
    )
    write_json(
        HERE,
        "sources.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            source_rows,
            outside_count=outside,
            ai_labs_count=shown(ai_total),
            ai_labs_share=share(shown(ai_total), outside),
            total_count=total,
            ended_from=src["ended_from"],
            note=(
                "came-from: the outside hires by a job that ended in 2025 or later, at the first employer in the "
                "listed order that matches, so the rows add up to outside_count; internships do not count for "
                "companies and do count for universities. ai_labs_count is the five AI labs together. "
                "ever-worked-at: the whole group by any past non-intern job at the employer; those rows overlap."
            ),
        ),
    )
    write_json(
        HERE,
        "roles.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            role_rows,
            total_count=total,
            stayed_count=c["stayed"],
            outside_count=outside,
            lab_research_count=lv_lab["total"],
            baseline_research_count=lv_base["total"],
            note=(
                "function: current_function for the whole group and each cohort; other is any other stated "
                "function. level-in-research: current_seniority among people whose current function is Research, "
                "in the lab and in the baseline of Meta's other research staff (no lab term in headline or title). "
                "doctorate: an education entry with degree Doctorate, finished or in progress."
            ),
        ),
    )
    write_json(
        HERE,
        "teams.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            team_rows,
            total_count=total,
            note=(
                "People who name a group of the lab in their headline or current title; a person can name more than "
                "one, so rows overlap and have no total. Most name no group. fair-only is outside the population."
            ),
        ),
    )
    write_json(
        HERE,
        "places.json",
        aggregate(
            "profiles",
            snap,
            SRC_BOTH,
            place_rows,
            total_count=total,
            us_count=us,
            us_share=share(us, total),
            note="Where people list themselves (location on the profile). The rows add up to total_count.",
        ),
    )
    write_json(
        HERE,
        "postings.json",
        aggregate(
            "jobs",
            snap,
            SRC_BOTH,
            posting_rows,
            meta_open_count=meta_open,
            share_of_meta_open=share(j_all, meta_open),
            note=(
                "Open Meta postings that name the lab in the title or description. Location rows use the "
                "posting's city or state and add up to all. The experience share is of postings that state one."
            ),
        ),
    )
    for name, doc2 in map_out.items():
        write_json(HERE, name, doc2)
    write_json(HERE, "receipt.json", p.receipt())

    print(f"{p.calls} calls, {p.spent()} Credits")
    print("cohorts", c, "narrow", nc, "microsoft", mc, "labeling", labeling)
    print(
        "first", list(zip(edges_all, first_all)), "job", list(zip(job_edges, first_job))
    )
    print("ms first", list(zip(cmp_["edges"], ms_first)), "moves", list(zip(mv, since)))
    print("sources", source_cells, "context", context_cells)
    print("functions", fn_all, fn_out, "levels", lv_lab, lv_base, "doctorate", doc)
    print("teams", teams, "fair only", fair_only, "places", us, states, bay, countries)
    print("jobs", jc, "meta open", meta_open)
    print("map units", {u: v.get("count") for u, v in m2["units"].items()})
    print("map size", m2["size"], "families", m2["families"])
    print("map flows", {k: v["all"] for k, v in m2["flows"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
