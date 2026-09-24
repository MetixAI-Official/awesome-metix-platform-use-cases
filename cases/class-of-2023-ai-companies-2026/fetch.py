#!/usr/bin/env python3
"""Reproduce this study: the AI companies founded after ChatGPT, and where their staff came from.

    export METIX_KEY=...   (your key; or put it in the repository's .env)
    python3 cases/class-of-2023-ai-companies-2026/fetch.py

Every company number is a count. Records are read for three things only: the
largest companies in two cohorts (to pick the ones whose staff are joined), a
slice of their staff (to check that a name finds the right company), and the
small teams with big rounds (to check each one by hand-written rules). The
definition and its audit are in queries/definition.json; the rest of queries/
holds every group, band, term list, and exclusion. Nothing is written to data/
until every count is in, so a stopped run leaves data/ as it was. Records go to
data/raw/, which git ignores.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from metix_client import MIN_CELL, Platform, aggregate, write_json

MAX_CREDITS = 3000
MIN_BASE = 30  # a share is published only when its denominator is at least 30


def q(name: str) -> dict:
    return json.loads((HERE / "queries" / f"{name}.json").read_text(encoding="utf-8"))


DEF = q("definition")
COH = q("cohorts")
PLACES = q("places")
THEMES = q("themes")
MEAS = q("measures")
STAFF = q("staff")


class Client(Platform):
    """The shared client, with a pause and retry when the rate limit is hit or the connection drops."""

    def request(self, method, path, body=None, *, billable=True):
        for attempt in range(8):
            try:
                return super().request(method, path, body, billable=billable)
            except SystemExit as err:
                if "429" not in str(err) or attempt == 7:
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
                # A dropped connection; a count that reached the server may be charged twice.
                if attempt == 7:
                    sys.exit(f"{method} {path} failed after retries: {err}")
            self.calls -= billable  # the call is sent again
            time.sleep(2 + 2 * attempt)
        raise AssertionError("unreachable")


# -- conditions -------------------------------------------------------------


def kw(terms: list[str]) -> dict:
    return {"any": [{"field": "keywords", "match": t} for t in terms]}


def f(field: str, op: str, value: object) -> dict:
    return {"field": field, op: value}


def between(field: str, lo: object = None, hi: object = None) -> list[dict]:
    out = []
    if lo is not None:
        out.append(f(field, "gte", lo))
    if hi is not None:
        out.append(f(field, "lte", hi))
    return out


def founded(lo: int, hi: int | None = None) -> list[dict]:
    return between("founded_year", lo, lo if hi is None else hi)


def missing(field: str) -> dict:
    return {"not": f(field, "exists", True)}


AI = DEF["where"]
ORG = {"not": f("type", "in", DEF["exclude_types"])}
NAME_PATH = {"all": [ORG, f("name", "match", DEF["name_word"]), kw(DEF["loose_terms"])]}
PROBE = kw(DEF["comparisons"]["probe"]["terms"])
LOOSE = kw(DEF["loose_terms"])
LOOSE_ORG = {"all": [ORG, LOOSE]}
TECH3 = {"all": [ORG, kw(DEF["comparisons"]["technical_neutral"]["terms"])]}
TECH5 = {"all": [ORG, kw(DEF["technical_terms"])]}
US = f("headquarters.country", "eq", "United States")

GROUPS = COH["groups"]


def group(gid: str) -> list[dict]:
    g = GROUPS[gid]
    return founded(g["from"], g["to"])


def share(part: object, whole: object) -> float | None:
    if isinstance(part, int) and isinstance(whole, int) and whole >= MIN_BASE:
        return round(part / whole, 4)
    return None


# -- counting ---------------------------------------------------------------


def exact(p: Platform, entity: str, conditions: list[dict]) -> int:
    n = p.count(entity, {"all": conditions})
    if not isinstance(n, int):
        sys.exit(
            f"Not written: a count came back banded ({n}) where none was expected."
        )
    return n


def splits() -> list[list[list[dict]]]:
    sizes = [[f("size", "eq", b)] for b in COH["size_bands"]] + [[missing("size")]]
    heads = [between("headcount", lo, hi) for lo, hi in COH["headcount_parts"]]
    heads.append([missing("headcount")])
    countries = [
        [US],
        [{"not": US}, f("headquarters.country", "exists", True)],
        [missing("headquarters.country")],
    ]
    return [sizes, heads, countries]


SPLITS = splits()


def total(p: Platform, conditions: list[dict], level: int = 0) -> tuple[int, int]:
    """A companies count, split into disjoint parts while it comes back banded.

    Returns the count and how many counts were added to make it."""
    n = p.count("companies", {"all": conditions})
    if isinstance(n, int):
        return n, 1
    if level == len(SPLITS):
        sys.exit(f"Not written: a count stayed banded after every split ({n}).")
    s, parts = 0, 0
    for part in SPLITS[level]:
        a, b = total(p, conditions + part, level + 1)
        s, parts = s + a, parts + b
    return s, parts


# -- 1. founding wave and lag -------------------------------------------------


def wave(p: Platform) -> tuple[list[dict], dict[int, int]]:
    lo, hi = COH["years"]
    rows, ai_by_year = [], {}
    for y in range(lo, hi + 1):
        yr = founded(y)
        ai = exact(p, "companies", yr + [AI])
        name_path = exact(p, "companies", yr + [NAME_PATH])
        probe = exact(p, "companies", yr + [PROBE])
        loose = exact(p, "companies", yr + [LOOSE])
        tech3 = exact(p, "companies", yr + [TECH3])
        tech5 = exact(p, "companies", yr + [TECH5])
        everyone, parts = total(p, yr)
        # The series that leave out nonprofits, educational institutions, and government
        # agencies are divided by every company of the same types; probe and loose keep
        # every type, so they are divided by every company.
        typed, typed_parts = total(p, yr + [ORG])
        ai_by_year[y] = ai
        rows.append(
            {
                "year": y,
                "ai_count": ai,
                "all_count": everyone,
                "all_parts": parts,
                "all_typed_count": typed,
                "all_typed_parts": typed_parts,
                "ai_share": share(ai, typed),
                "name_path_count": name_path,
                "name_path_share": share(name_path, typed),
                "probe_count": probe,
                "probe_share": share(probe, everyone),
                "loose_count": loose,
                "loose_share": share(loose, everyone),
                "technical_neutral_count": tech3,
                "technical_neutral_share": share(tech3, typed),
                "technical_count": tech5,
                "technical_share": share(tech5, typed),
            }
        )
    return rows, ai_by_year


def lag(p: Platform, ai_by_year: dict[int, int]) -> list[dict]:
    lo, hi = COH["theme_years"]
    rows = []
    for y in range(lo, hi + 1):
        base = founded(y) + [AI]
        row = {"year": y, "ai_count": ai_by_year[y]}
        for b in COH["lag"]["updated_buckets"]:
            row[f"updated_{b['id'].replace('-', '_')}_count"] = exact(
                p, "companies", base + between("updated_at", b.get("gte"), b.get("lte"))
            )
        row["headcount_count"] = exact(
            p, "companies", base + [f("headcount", "exists", True)]
        )
        row["headcount_11_count"] = exact(
            p, "companies", base + [f("headcount", "gte", 11)]
        )
        row["headcount_share"] = share(row["headcount_count"], ai_by_year[y])
        row["headcount_11_share"] = share(row["headcount_11_count"], ai_by_year[y])
        rows.append(row)
    return rows


# -- 2. geography -------------------------------------------------------------


def countries(p: Platform) -> tuple[list[dict], list[dict], list[str]]:
    rows, notes = [], []
    for gid in ("before", "class"):
        base = group(gid) + [AI]
        cohort = exact(p, "companies", base)
        known = exact(
            p, "companies", base + [f("headquarters.country", "exists", True)]
        )
        counts = {
            c: exact(p, "companies", base + [f("headquarters.country", "eq", c)])
            for c in PLACES["countries"]
        }
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        top = ranked[:15]
        fifteenth = top[-1][1]
        unlisted = known - sum(counts.values())
        if ranked[15][1] >= fifteenth or unlisted >= fifteenth:
            notes.append(
                f"{gid}: a country outside the top 15 could tie or rank; check the list"
            )
        for rank, (c, n) in enumerate(top, 1):
            rows.append(
                {
                    "cohort": gid,
                    "group": c,
                    "rank": rank,
                    "count": n,
                    "share": share(n, cohort),
                    "share_of_known": share(n, known),
                }
            )
        rest = known - sum(n for _, n in top)
        rows.append(
            {
                "cohort": gid,
                "group": "rest",
                "count": rest,
                "share": share(rest, cohort),
                "share_of_known": share(rest, known),
            }
        )
        rows.append(
            {
                "cohort": gid,
                "group": "no-country",
                "count": cohort - known,
                "share": share(cohort - known, cohort),
            }
        )
        rows.append(
            {"cohort": gid, "group": "total", "count": cohort, "known_count": known}
        )
        notes.append(
            f"{gid}: the largest candidate not shown has {ranked[15][1]}; "
            f"companies in no candidate country: {unlisted}"
        )
    china = []
    lo, hi = COH["theme_years"]
    cn = f("headquarters.country", "eq", "China")
    for y in range(lo, hi + 1):
        everyone, _ = total(p, founded(y) + [cn])
        china.append(
            {
                "year": y,
                "all_count": everyone,
                "ai_count": exact(p, "companies", founded(y) + [cn, AI]),
            }
        )
    return rows, china, notes


def city(names: list[str]) -> dict:
    # in matches each name word by word, like match, in one condition.
    return f("headquarters.city", "in", names)


def metro_where(m: dict) -> dict:
    country = f("headquarters.country", "eq", m["country"])
    if not m.get("cities"):
        return country
    options = []
    if m.get("state"):
        state = f("headquarters.state", "match", m["state"])
        options.append(
            {
                "all": [
                    city(m["cities"]),
                    {"any": [state, missing("headquarters.state")]},
                ]
            }
        )
        if m.get("strict_cities"):
            options.append({"all": [city(m["strict_cities"]), state]})
    else:
        options.append(city(m["cities"]))
    return {"all": [country, {"any": options}]}


def metro_comparison(p: Platform) -> list[dict]:
    """SF Bay Area, the city of San Francisco, and London under the comparison definitions."""
    by_id = {m["id"]: m for m in PLACES["metros"]}
    places = {
        "sf-bay-area": metro_where(by_id["sf-bay-area"]),
        "san-francisco-city": {
            "all": [US, f("headquarters.city", "match", "San Francisco")]
        },
        "london": metro_where(by_id["london"]),
    }
    rows = []
    for name, d in (("definition", AI), ("probe", PROBE), ("loose", LOOSE)):
        for gid in ("before", "class"):
            base = group(gid) + [d]
            cohort = exact(p, "companies", base)
            with_city = exact(
                p, "companies", base + [f("headquarters.city", "exists", True)]
            )
            row = {
                "definition": name,
                "cohort": gid,
                "count": cohort,
                "city_count": with_city,
            }
            for pid, where in places.items():
                n = exact(p, "companies", base + [where])
                row[f"{pid}_count"] = n
                row[f"{pid}_share"] = share(n, cohort)
                row[f"{pid}_share_of_city"] = share(n, with_city)
            rows.append(row)
    return rows


def metros(p: Platform) -> list[dict]:
    rows = []
    for gid in ("before", "class"):
        base = group(gid) + [AI]
        cohort = exact(p, "companies", base)
        with_city = exact(
            p, "companies", base + [f("headquarters.city", "exists", True)]
        )
        for m in PLACES["metros"]:
            n = exact(p, "companies", base + [metro_where(m)])
            rows.append(
                {
                    "cohort": gid,
                    "group": m["id"],
                    "count": n,
                    "share": share(n, cohort),
                    "share_of_city": share(n, with_city),
                }
            )
        rows.append(
            {
                "cohort": gid,
                "group": "total",
                "count": cohort,
                "city_count": with_city,
                "city_share": share(with_city, cohort),
            }
        )
    return rows


# -- 3. themes and industries ------------------------------------------------------


def theme_where(t: dict) -> dict:
    parts = [kw(t["terms"])]
    if t.get("exclude"):
        parts.append({"not": kw(t["exclude"])})
    return {"all": parts}


def themes(p: Platform, ai_by_year: dict[int, int]) -> list[dict]:
    lo, hi = COH["theme_years"]
    rows = []
    for y in range(lo, hi + 1):
        loose = exact(p, "companies", founded(y) + [LOOSE_ORG])
        for t in THEMES["themes"]:
            n = exact(p, "companies", founded(y) + [AI, theme_where(t)])
            nl = exact(p, "companies", founded(y) + [LOOSE_ORG, theme_where(t)])
            rows.append(
                {
                    "year": y,
                    "group": t["id"],
                    "count": n,
                    "ai_count": ai_by_year[y],
                    "share": share(n, ai_by_year[y]),
                    "loose_count": nl,
                    "loose_base_count": loose,
                    "loose_share": share(nl, loose),
                }
            )
    return rows


def words(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def industries(p: Platform) -> list[dict]:
    cands = MEAS["industries"]["candidates"]
    rows = []
    for gid in ("before", "class"):
        base = group(gid) + [AI]
        cohort = exact(p, "companies", base)
        listed = 0
        for v in cands:
            longer = [w for w in cands if w != v and words(v) < words(w)]
            cond = [f("industry", "match", v)]
            if longer:
                cond.append(
                    {"not": {"any": [f("industry", "match", w) for w in longer]}}
                )
            n = exact(p, "companies", base + cond)
            listed += n
            rows.append(
                {"cohort": gid, "group": v, "count": n, "share": share(n, cohort)}
            )
        rows.append(
            {
                "cohort": gid,
                "group": "rest",
                "count": cohort - listed,
                "share": share(cohort - listed, cohort),
            }
        )
        rows.append({"cohort": gid, "group": "total", "count": cohort})
    return rows


# -- 4. size and growth -------------------------------------------------------------


def sizes(p: Platform, ai_by_year: dict[int, int]) -> list[dict]:
    lo, hi = COH["theme_years"]
    rows = []
    for y in range(lo, hi + 1):
        base = founded(y) + [AI]
        parts = {
            b: exact(p, "companies", base + [f("size", "eq", b)])
            for b in MEAS["size"]["bands"]
        }
        parts["none"] = exact(p, "companies", base + [missing("size")])
        if sum(parts.values()) != ai_by_year[y]:
            sys.exit(
                f"Not written: size bands for {y} do not add up to the year's count."
            )
        for b, n in parts.items():
            rows.append(
                {"year": y, "group": b, "count": n, "share": share(n, ai_by_year[y])}
            )
    return rows


def growth(p: Platform) -> list[dict]:
    g = MEAS["growth"]
    field = "headcount_growth_yoy_pct"
    rows = []
    for gid in ("before", "class"):
        base = group(gid) + [AI, f("headcount", "gte", g["min_headcount"])]
        cohort = exact(p, "companies", base)
        parts = {}
        for b in g["bands"]:
            cond = []
            if "gte" in b:
                cond.append(f(field, "gte", b["gte"]))
            if "lt" in b:
                cond.append(f(field, "lt", b["lt"]))
            parts[b["id"]] = exact(p, "companies", base + cond)
        parts["not-stated"] = exact(p, "companies", base + [missing(field)])
        if sum(parts.values()) != cohort:
            sys.exit(f"Not written: growth bands for {gid} do not add up.")
        for b, n in parts.items():
            rows.append(
                {"cohort": gid, "group": b, "count": n, "share": share(n, cohort)}
            )
        stated = cohort - parts["not-stated"]
        for b, n in parts.items():
            if b != "not-stated":
                rows[-len(parts) + list(parts).index(b)]["share_of_stated"] = share(
                    n, stated
                )
        rows.append(
            {"cohort": gid, "group": "total", "count": cohort, "stated_count": stated}
        )
    return rows


# -- 5. funding ---------------------------------------------------------------------


def quarters() -> list[tuple[str, str, str]]:
    (a, b) = MEAS["funding"]["quarters"]
    y, qn = int(a[:4]), int(a[-1])
    out = []
    while True:
        start = f"{y}-{3 * qn - 2:02d}-01"
        end_month = 3 * qn
        last = {3: 31, 6: 30, 9: 30, 12: 31}[end_month]
        out.append((f"{y}Q{qn}", start, f"{y}-{end_month:02d}-{last}"))
        if f"{y}Q{qn}" == b:
            return out
        qn += 1
        if qn == 5:
            y, qn = y + 1, 1


def funding(p: Platform) -> tuple[list[dict], list[dict], list[dict]]:
    cover = []
    for gid in GROUPS:
        base = group(gid) + [AI]
        cohort = exact(p, "companies", base)
        dated = exact(p, "companies", base + [f("last_funding.date", "exists", True)])
        amount = exact(
            p, "companies", base + [f("last_funding.amount", "exists", True)]
        )
        us = exact(p, "companies", base + [US])
        us_amount = exact(
            p, "companies", base + [US, f("last_funding.amount", "exists", True)]
        )
        cover.append(
            {
                "cohort": gid,
                "us_count": us,
                "us_amount_count": us_amount,
                "us_amount_share": share(us_amount, us),
                "count": cohort,
                "dated_count": dated,
                "dated_share": share(dated, cohort),
                "amount_count": amount,
                "amount_share": share(amount, cohort),
            }
        )
    by_q = []
    for label, start, end in quarters():
        rng = between("last_funding.date", start, end)
        by_q.append(
            {
                "quarter": label,
                "all_years_count": exact(p, "companies", [AI] + rng),
                "class_count": exact(p, "companies", [AI] + group("class") + rng),
            }
        )
    amounts = []
    for gid in ("before", "class"):
        base = group(gid) + [AI, US]
        stated = exact(
            p, "companies", base + [f("last_funding.amount", "exists", True)]
        )
        parts = {}
        for b in MEAS["funding"]["amount_bands"]:
            cond = []
            if "gte" in b:
                cond.append(f("last_funding.amount", "gte", b["gte"]))
            if "lt" in b:
                cond.append(f("last_funding.amount", "lt", b["lt"]))
            parts[b["id"]] = exact(p, "companies", base + cond)
        if sum(parts.values()) != stated:
            sys.exit(f"Not written: amount bands for {gid} do not add up.")
        for b, n in parts.items():
            amounts.append(
                {"cohort": gid, "group": b, "count": n, "share": share(n, stated)}
            )
        amounts.append({"cohort": gid, "group": "total", "count": stated})
    return cover, by_q, amounts


# -- 5b. controls: every company, the same measures ---------------------------------------


def cohort_total(p: Platform, gid: str, conditions: list[dict]) -> int:
    """All companies in a cohort, one founding year at a time, split when banded."""
    g = GROUPS[gid]
    return sum(
        total(p, founded(y) + conditions)[0] for y in range(g["from"], g["to"] + 1)
    )


def ranges(field: str, b: dict) -> list[dict]:
    out = []
    if "gte" in b:
        out.append(f(field, "gte", b["gte"]))
    if "lt" in b:
        out.append(f(field, "lt", b["lt"]))
    return out


def control_row(
    measure: str,
    key: str,
    value: object,
    group_: str,
    all_n: int,
    ai_n: int,
    all_base: int,
    ai_base: int,
) -> dict:
    non, non_base = all_n - ai_n, all_base - ai_base
    return {
        "measure": measure,
        key: value,
        "group": group_,
        "all_count": all_n,
        "ai_count": ai_n,
        "non_ai_count": non,
        "all_share": share(all_n, all_base),
        "ai_share": share(ai_n, ai_base),
        "non_ai_share": share(non, non_base),
    }


def controls(
    p: Platform,
    growth_rows: list[dict],
    cover: list[dict],
    amounts: list[dict],
    size_rows: list[dict],
) -> list[dict]:
    """Every company of the same type (no AI filter), for growth, funding, and size.

    ai_count repeats the AI figure from the measure's own file; non_ai is all minus AI."""
    rows = []
    field = "headcount_growth_yoy_pct"
    g = MEAS["growth"]
    for gid in ("before", "class"):
        base = [ORG, f("headcount", "gte", g["min_headcount"])]
        ai = {r["group"]: r["count"] for r in growth_rows if r["cohort"] == gid}
        parts = {
            b["id"]: cohort_total(p, gid, base + ranges(field, b)) for b in g["bands"]
        }
        parts["not-stated"] = cohort_total(p, gid, base + [missing(field)])
        all_base = sum(parts.values())
        stated_all = all_base - parts["not-stated"]
        stated_ai = ai["total"] - ai["not-stated"]
        for b, n in parts.items():
            if b == "not-stated":
                rows.append(
                    control_row(
                        "growth", "cohort", gid, b, n, ai[b], all_base, ai["total"]
                    )
                )
            else:
                rows.append(
                    control_row(
                        "growth", "cohort", gid, b, n, ai[b], stated_all, stated_ai
                    )
                )
        rows.append(
            control_row(
                "growth",
                "cohort",
                gid,
                "total",
                all_base,
                ai["total"],
                all_base,
                ai["total"],
            )
        )
    for c in cover:
        gid = c["cohort"]
        everyone = cohort_total(p, gid, [ORG])
        dated = cohort_total(p, gid, [ORG, f("last_funding.date", "exists", True)])
        amount = cohort_total(p, gid, [ORG, f("last_funding.amount", "exists", True)])
        rows.append(
            control_row(
                "funding",
                "cohort",
                gid,
                "dated",
                dated,
                c["dated_count"],
                everyone,
                c["count"],
            )
        )
        rows.append(
            control_row(
                "funding",
                "cohort",
                gid,
                "amount",
                amount,
                c["amount_count"],
                everyone,
                c["count"],
            )
        )
        rows.append(
            control_row(
                "funding",
                "cohort",
                gid,
                "total",
                everyone,
                c["count"],
                everyone,
                c["count"],
            )
        )
    for gid in ("before", "class"):
        ai = {r["group"]: r["count"] for r in amounts if r["cohort"] == gid}
        base = [ORG, US]
        parts = {
            b["id"]: cohort_total(p, gid, base + ranges("last_funding.amount", b))
            for b in MEAS["funding"]["amount_bands"]
        }
        stated = sum(parts.values())
        for b, n in parts.items():
            rows.append(
                control_row(
                    "us-amount", "cohort", gid, b, n, ai[b], stated, ai["total"]
                )
            )
        rows.append(
            control_row(
                "us-amount",
                "cohort",
                gid,
                "total",
                stated,
                ai["total"],
                stated,
                ai["total"],
            )
        )
    lo, hi = COH["theme_years"]
    for y in range(lo, hi + 1):
        ai = {r["group"]: r["count"] for r in size_rows if r["year"] == y}
        parts = {
            b: total(p, founded(y) + [ORG, f("size", "eq", b)])[0]
            for b in MEAS["size"]["bands"]
        }
        parts["none"] = total(p, founded(y) + [ORG, missing("size")])[0]
        everyone = sum(parts.values())
        ai_all = sum(ai.values())
        for b, n in parts.items():
            rows.append(control_row("size", "year", y, b, n, ai[b], everyone, ai_all))
        rows.append(
            control_row("size", "year", y, "total", everyone, ai_all, everyone, ai_all)
        )
    return rows


# -- 6. small teams, big rounds -----------------------------------------------------------


def band(n: int, edges: list[tuple[int, str]]) -> str:
    label = edges[0][1]
    for edge, name in edges:
        if n >= edge:
            label = name
    return label


def lean(p: Platform) -> tuple[list[dict], list[dict], list[dict]]:
    L = MEAS["lean"]
    since = [f("founded_year", "gte", L["founded_from"]), US]
    counts = []
    for which, d in (("definition", AI), ("loose", LOOSE)):
        for hc in L["also_counted"]["headcount_max"]:
            for amt in L["also_counted"]["amount_min"]:
                counts.append(
                    {
                        "group": f"{which}-headcount-{hc}-amount-{amt // 1_000_000}m",
                        "definition": which,
                        "headcount_max": hc,
                        "amount_min": amt,
                        "count": exact(
                            p,
                            "companies",
                            [d]
                            + since
                            + [
                                f("headcount", "lte", hc),
                                f("last_funding.amount", "gte", amt),
                            ],
                        ),
                    }
                )
    where = {
        "all": [LOOSE]
        + since
        + [
            f("headcount", "lte", L["headcount_max"]),
            f("last_funding.amount", "gte", L["amount_min"]),
        ]
    }
    ids, _ = p.search_all("companies", {"where": where, "size": 100})
    recs = p.detail(
        "companies",
        ids,
        [
            "id",
            "name",
            "founded_year",
            "headcount",
            "size",
            "headquarters",
            "last_funding",
            "keywords",
            "industry",
            "website",
            "type",
        ],
    )
    raw, rows, dropped = [], [], []
    for r in recs:
        lf = r.get("last_funding") or {}
        amount, date = lf.get("amount"), lf.get("date") or ""
        reason = L["excluded"].get(r["name"])
        if not reason and date and int(date[:4]) < r["founded_year"]:
            reason = "the round predates the founding year on the record"
        if not reason and amount and amount >= 1_000_000_000:
            reason = "a round of a billion or more for a team of 50 or fewer: taken as a data error"
        raw.append({**r, "kept": reason is None, "reason": reason})
        if reason:
            dropped.append({"company": r["name"], "reason": reason})
            continue
        rows.append(
            {
                "company": r["name"],
                "founded_year": r["founded_year"],
                "headcount_band": band(
                    r.get("headcount") or 0, [(0, "1-10"), (11, "11-25"), (26, "26-50")]
                ),
                "hq_country": (r.get("headquarters") or {}).get("country"),
                "amount_band": band(
                    amount,
                    [
                        (50_000_000, "50m-100m"),
                        (100_000_000, "100m-250m"),
                        (250_000_000, "250m-1b"),
                    ],
                ),
                "month": date[:7],
            }
        )
    rows.sort(key=lambda r: (r["month"], r["company"]), reverse=True)
    raw_dir = HERE / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "lean.json").write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return counts, rows, dropped


# -- 7. where the staff came from ------------------------------------------------------------


def current(names: list[str]) -> dict:
    return {
        "has_experience": {
            "all": [
                f("experience.company.name", "in", names),
                f("experience.is_current", "eq", True),
            ]
        }
    }


def earlier(names: list[str]) -> dict:
    return {
        "has_experience": {
            "all": [
                f("experience.company.name", "in", names),
                f("experience.is_current", "eq", False),
                {"not": f("experience.seniority", "eq", "Intern")},
                {"not": f("experience.title", "match", "intern")},
            ]
        }
    }


def staff_cohort(p: Platform, key: str, cfg: dict, raw: dict) -> dict:
    where = {
        "all": [AI]
        + founded(cfg["from"], cfg["to"])
        + [f("headcount", "gte", cfg["headcount_min"])]
    }
    ids, _ = p.search_all("companies", {"where": where, "size": 1000})
    recs = p.detail("companies", ids, ["id", "name", "headcount", "founded_year"])
    recs.sort(key=lambda r: -(r.get("headcount") or 0))
    top = recs[: cfg["top"]]
    skip = STAFF["not_companies"][key]
    picked = [r for r in top if r["name"] not in skip]
    not_companies = len(top) - len(picked)
    # Hand verdicts (queries/staff.json): only Y, V, and L companies are joined.
    verdicts = STAFF["verdicts"][key]
    unclassified = [r["name"] for r in picked if r["name"] not in verdicts]
    excluded = [r["name"] for r in picked if verdicts.get(r["name"]) in ("G", "N")]
    picked = [r for r in picked if verdicts.get(r["name"]) in ("Y", "V", "L")]
    # Screen: a name that finds far more current profiles than the company's headcount is shared.
    kept = []
    for r in picked:
        n = p.count("people", current([r["name"]]))
        r["profiles"] = n
        r["screen"] = (
            isinstance(n, int)
            and 0 < n <= STAFF["screen"]["max_ratio"] * r["headcount"]
        )
        if r["screen"]:
            kept.append(r)
    # Id check on one whole slice of the kept names' staff.
    lo, hi = STAFF["id_check"][
        f"{key}_window" if key != "baseline" else "baseline_window"
    ]
    names = [r["name"] for r in kept]
    id_of = {r["name"]: r["id"] for r in kept}
    sample_where = {
        "all": [current(names)] + between("total_experience_months", lo, hi)
    }
    pids, _ = p.search_all("people", {"where": sample_where, "size": 1000})
    people = p.detail(
        "people",
        pids,
        ["experience.company.id", "experience.company.name", "experience.is_current"],
    )
    seen: dict[str, list[int]] = {}
    passed = 0
    for person in people:
        ok = False
        for e in person.get("experience") or []:
            if not e.get("is_current"):
                continue
            c = e.get("company") or {}
            for n in names:
                if words(n) <= words(c.get("name") or ""):
                    hit = c.get("id") == id_of[n]
                    seen.setdefault(n, [0, 0])
                    seen[n][0] += hit
                    seen[n][1] += 1
                    ok = ok or hit
        passed += ok
    failed = [n for n, (good, all_) in seen.items() if all_ >= 2 and good * 2 < all_]
    final = [n for n in names if n not in failed]
    raw[key] = {
        "verdict_excluded": excluded,
        "unclassified": unclassified,
        "top": top,
        "failed_id_check": failed,
        "sample_by_name": seen,
    }
    return {
        "read": len(recs),
        "top": len(top),
        "not_companies": not_companies,
        "screened_out": len(picked) - len(kept),
        "failed_id_check": failed,
        "kept": final,
        "labeling": [n for n in final if verdicts.get(n) == "L"],
        "verdict_excluded": excluded,
        "unclassified": unclassified,
        "sample_count": len(people),
        "sample_pass_count": passed,
        "headcount_of_smallest": top[-1]["headcount"] if top else None,
    }


def staff(p: Platform) -> tuple[list[dict], list[dict], list[dict], list[str]]:
    raw: dict = {}
    rows, cohorts, checks, problems = [], [], [], []
    for key, cfg in STAFF["cohorts"].items():
        info = staff_cohort(p, key, cfg, raw)
        sets = {
            "all": info["kept"],
            "without-labeling": [n for n in info["kept"] if n not in info["labeling"]],
        }
        found: dict[str, dict] = {}
        for set_id, names_ in sets.items():
            cur = current(names_)
            c = {"total": exact(p, "people", [cur])}
            for e in STAFF["employers"]:
                if key in e.get("not_for", []):
                    continue
                c[e["id"]] = exact(p, "people", [cur, earlier(e["names"])])
            for rid, members in STAFF["rollups"].items():
                names = [
                    n
                    for e in STAFF["employers"]
                    if e["id"] in members
                    for n in e["names"]
                ]
                c[rid] = exact(p, "people", [cur, earlier(names)])
            c["founder-title"] = exact(
                p, "people", [cur, f("current_title", "match", "founder")]
            )
            found[set_id] = c

        def small(v: int) -> bool:
            return 0 < v < MIN_CELL

        shown: dict[str, dict] = {sid: {} for sid in found}
        for sid, c in found.items():
            for g, n in c.items():
                shown[sid][g] = "<10" if small(n) else n
            for rid, members in STAFF["rollups"].items():
                vis = sum(c[m] for m in members if m in c and not small(c[m]))
                gap = abs(c[rid] - vis)
                if small(c[rid]) or small(gap):
                    shown[sid][rid] = None
                    problems.append(
                        f"{key} {sid} {rid}: withheld, it differs from its shown members by {gap}"
                    )
        # The two sets differ by the staff of the labeling companies: a difference of 1 to 9
        # would publish a small group, so the smaller set's cell is withheld.
        for g in found["all"]:
            a, b = shown["all"][g], shown["without-labeling"][g]
            if isinstance(a, int) and isinstance(b, int) and small(a - b):
                shown["without-labeling"][g] = None
                problems.append(
                    f"{key} without-labeling {g}: withheld, it differs from the all set by {a - b}"
                )
        for sid, c in found.items():
            for g, n in c.items():
                if g == "total":
                    continue
                kind = (
                    "rollup"
                    if g in STAFF["rollups"]
                    else "current-title"
                    if g == "founder-title"
                    else "employer"
                )
                v = shown[sid][g]
                rows.append(
                    {
                        "cohort": key,
                        "set": sid,
                        "group": g,
                        "kind": kind,
                        "count": v,
                        "share": share(v, c["total"]) if isinstance(v, int) else None,
                    }
                )
            rows.append(
                {
                    "cohort": key,
                    "set": sid,
                    "group": "total",
                    "kind": "total",
                    "count": c["total"],
                }
            )
        checks.append(
            {
                "cohort": key,
                "id_sample_count": info["sample_count"],
                "id_pass_count": info["sample_pass_count"],
                "id_pass_share": share(info["sample_pass_count"], info["sample_count"]),
            }
        )
        cohorts.append(
            {
                "cohort": key,
                "companies_read_count": info["read"],
                "top_count": info["top"],
                "not_companies_count": info["not_companies"],
                "screened_out_count": info["screened_out"],
                "failed_id_check_count": len(info["failed_id_check"]),
                "verdict_excluded_count": len(info["verdict_excluded"]),
                "unclassified_count": len(info["unclassified"]),
                "kept_companies_count": len(info["kept"]),
                "labeling_companies_count": len(info["labeling"]),
                "smallest_headcount_in_top": info["headcount_of_smallest"],
                "companies": info["kept"],
                "labeling_companies": info["labeling"],
                "verdict_excluded": info["verdict_excluded"],
                "unclassified": info["unclassified"],
            }
        )
    raw_dir = HERE / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "staff.json").write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return rows, cohorts, checks, problems


# -- main ------------------------------------------------------------------------------------


def main() -> int:
    p = Client(max_credits=MAX_CREDITS)
    snap = p.snapshot
    out: dict[str, dict] = {}

    wave_rows, ai_by_year = wave(p)
    out["wave.json"] = aggregate(
        "companies",
        snap,
        "queries/definition.json · queries/cohorts.json",
        wave_rows,
        note=(
            "Companies by founding year. ai_count uses the definition; name_path, probe, loose, "
            "technical_neutral, and technical are the comparison definitions in queries/definition.json. all_count is every company "
            "founded that year, added up from all_parts disjoint counts when the total is banded; all_typed_count is the same "
            "for every company whose type is not Nonprofit, Educational, or Government Agency. ai, name_path, technical_neutral, "
            "and technical leave those types out, so their shares are of all_typed_count; probe and loose keep every type, so "
            "their shares are of all_count."
        ),
    )
    out["lag.json"] = aggregate(
        "companies",
        snap,
        "queries/cohorts.json",
        lag(p, ai_by_year),
        note=(
            "AI companies by founding year: when the record was last refreshed (updated_at month), "
            "and how many carry a headcount, and one of 11 or more."
        ),
    )
    c_rows, china, c_notes = countries(p)
    out["countries.json"] = aggregate(
        "companies",
        snap,
        "queries/places.json",
        c_rows,
        note="AI companies by headquarters country, top 15 per cohort; rest and no-country complete each cohort. "
        + " ".join(c_notes),
        coverage=china,
        coverage_note="All companies and AI companies headquartered in China, by founding year.",
    )
    out["metros.json"] = aggregate(
        "companies",
        snap,
        "queries/places.json",
        metros(p),
        note=(
            "AI companies by headquarters metro. share is of the whole cohort, share_of_city of the "
            "companies that give a city; city_share is how many give one. comparison repeats the SF Bay "
            "Area, the city of San Francisco, and London under the probe and loose definitions."
        ),
        comparison=metro_comparison(p),
    )
    out["themes.json"] = aggregate(
        "companies",
        snap,
        "queries/themes.json",
        themes(p, ai_by_year),
        note=(
            "Share of each founding year's AI companies whose tags name the theme (share), and the same "
            "inside the loose population, any of the nine loose terms with the same type exclusion "
            "(loose_share). Themes overlap. Four themes are also entry terms of the definition, so compare "
            "their movement, not their level."
        ),
    )
    out["industries.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        industries(p),
        note=MEAS["industries"]["note"],
    )
    size_rows = sizes(p, ai_by_year)
    out["size.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        size_rows,
        note="AI companies by size band and founding year; none has no band.",
    )
    growth_rows = growth(p)
    out["growth.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        growth_rows,
        note="AI companies with headcount 11 or more, by year-on-year headcount change. share is of all; share_of_stated leaves out not-stated.",
    )
    cover, by_q, amounts = funding(p)
    out["funding.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        cover,
        note="How many AI companies in each cohort have a latest funding round with a date and with an amount. last_funding is the latest round only.",
        quarters=by_q,
        quarters_note=(
            "AI companies whose latest round is dated in the quarter: all founding years, and the class. "
            "Rounds stop after 2026Q1 (3 in 2026Q2, none in 2026Q3) because the company records were last "
            "refreshed in April and May 2026 (lag.json); a chart should end at 2026Q1, and 2026Q1 itself "
            "may be incomplete."
        ),
        amounts=amounts,
        amounts_note="United States headquarters only, because amounts elsewhere are often in local currency. Shares are of the companies with an amount.",
    )
    out["controls.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        controls(p, growth_rows, cover, amounts, size_rows),
        note=(
            "The growth, funding, US amount, and size measures for every company of the same types "
            "(Nonprofit, Educational, and Government Agency excluded), with no AI filter, beside the AI "
            "figures and all minus AI. Growth band shares are of the companies that state a figure "
            "(not-stated of all); us-amount shares are of US companies with an amount; funding shares "
            "are of the cohort; size shares are of the year."
        ),
    )
    lean_counts, lean_rows, lean_dropped = lean(p)
    out["lean.json"] = aggregate(
        "companies",
        snap,
        "queries/measures.json",
        lean_rows,
        note=(
            "AI companies headquartered in the United States, founded 2022 or later, with a headcount of 50 or "
            "less and a latest round of 50,000,000 or more that pass the checks in queries/measures.json. "
            "Bands and months only; names refer to the company."
        ),
        counts=lean_counts,
        dropped=lean_dropped,
    )
    s_rows, s_cohorts, s_checks, s_problems = staff(p)
    out["staff.json"] = aggregate(
        "profiles",
        snap,
        "queries/staff.json",
        s_rows,
        note=(
            "People with a current job at the largest AI companies of each cohort, by earlier employer. set all joins every kept company; set without-labeling leaves out the data-labeling marketplaces (queries/staff.json). "
            "Rows overlap and are not added. Counts are profiles visible through the Metix AI Platform, "
            "never a headcount. " + " ".join(s_problems)
        ),
        id_check=s_checks,
    )
    out["staff_companies.json"] = aggregate(
        "companies",
        snap,
        "queries/staff.json",
        s_cohorts,
        note=(
            "How the companies whose staff are counted in staff.json were chosen: read, the largest 150, "
            "those that are not companies, names screened out as shared, names that failed the id check, "
            "and the names kept. verdict_excluded are the G and N companies of the hand classification (queries/staff.json); unclassified are the names the classification run had already dropped (shared names over the 1.5 ratio, and Dify, which failed the id check), which are not joined."
        ),
    )

    for name, doc in out.items():
        write_json(HERE, name, doc)
    write_json(HERE, "receipt.json", p.receipt())
    print(
        f"{p.calls} calls, {p.results} results, {p.records} records, {p.spent()} Credits"
    )
    for r in wave_rows:
        print(r["year"], r["ai_count"], r["all_count"], r["ai_share"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
