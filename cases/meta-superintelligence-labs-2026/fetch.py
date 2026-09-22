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
"""

from __future__ import annotations

import json
import sys
from itertools import pairwise
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import MIN_CELL, Platform, aggregate, write_json

POP = json.loads((HERE / "queries" / "population.json").read_text(encoding="utf-8"))
MEAS = json.loads((HERE / "queries" / "measures.json").read_text(encoding="utf-8"))
SRC_POP = "queries/population.json"
SRC_BOTH = "queries/population.json · queries/measures.json"
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


def main() -> int:
    p = Platform(max_credits=130)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
