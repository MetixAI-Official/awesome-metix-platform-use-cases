#!/usr/bin/env python3
"""Fail when a file about to be published breaks the public data policy.

    python3 scripts/check_public.py            every tracked and untracked file
    python3 scripts/check_public.py --staged   only the staged content
    python3 scripts/check_public.py PATH ...   the given files

Each finding prints as path:line: rule: message. The matched text is never
printed, because Actions logs on a public repository are public too.

Internal terms come from the PUBLIC_CHECK_DENYLIST environment variable (one
term per line) and from .public-denylist in the repository root. Neither is
committed.

A line may opt out of one line rule for a documented reason with an inline
"check-public: allow <rule>" comment. Rules on files under cases/*/data/
cannot be opted out of.

The rules are explained in docs/public-data-policy.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DENYLIST_FILE = ".public-denylist"
DENYLIST_ENV = "PUBLIC_CHECK_DENYLIST"
MIN_CELL = 10
UNITS = {"profiles", "jobs", "companies"}

PRAGMA = re.compile(
    r"check-public:\s*allow\s+([a-z][a-z0-9_-]*(?:\s*,\s*[a-z][a-z0-9_-]*)*)"
)
DATA_PATH = re.compile(r"^cases/[^/]+/data/")
RAW_PATH = re.compile(r"^cases/[^/]+/data/raw/")
JSON_KEY = re.compile(r'"([^"\\]+)"\s*:')
PERSON_KEY = re.compile(
    r"^(?:name|full_?name|first_?name|last_?name|person_?name|"
    r"profile_?(?:id|url|link)|person_?id|linkedin(?:_?(?:id|key|url))?|"
    r"e_?mails?|email_?address|phones?|phone_?number|mobile|"
    r"photo(?:_?url)?|avatar(?:_?url)?|address|street)$",
    re.IGNORECASE,
)
# Numbers a profiles aggregate may hold besides counts: shares, statistics, and
# numeric dimensions such as a year. Any other numeric key is rejected.
NUMERIC_KEY = re.compile(
    r"^(?:min_cell|year|month|quarter|rank|share|pct|percent|ratio|mean|median|p\d{1,2})$"
    r"|^(?:share|pct|mean|median|p\d{1,2})_"
    r"|_(?:share|pct|percent|ratio|mean|median|p\d{1,2}|year|month|rank)$"
)

ALLOWED_EMAILS = {"support@metix.ai", "git@github.com"}
PLACEHOLDER_DOMAINS = (
    "example.com",
    "example.org",
    "example.net",
    "users.noreply.github.com",
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int | None
    rule: str
    message: str

    def format(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{where}: {self.rule}: {self.message}"


@dataclass(frozen=True)
class LineRule:
    name: str
    pattern: re.Pattern[str]
    message: str
    # Returns True when a match is acceptable after all, such as a placeholder.
    accept: Callable[[str], bool] | None = None


def _email_ok(text: str) -> bool:
    text = text.lower()
    return text in ALLOWED_EMAILS or text.endswith(PLACEHOLDER_DOMAINS)


def _phone_ok(text: str) -> bool:
    digits = sum(ch.isdigit() for ch in text)
    return not 9 <= digits <= 15


def _placeholder_ok(text: str) -> bool:
    value = re.split(r"[:=]", text, maxsplit=1)[-1].strip().strip("\"'")
    return "xxxx" in value.lower() or value.startswith(("$", "<", "{"))


LINE_RULES: tuple[LineRule, ...] = (
    LineRule(
        "key",
        re.compile(r"\b(?:metix|mira)_[A-Za-z0-9]{24,}\b"),
        "Metix AI Platform API key",
    ),
    LineRule(
        "credential",
        re.compile(
            r"sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
            r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}"
            r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?i:bearer\s+[A-Za-z0-9._~+/=-]{20,})"
        ),
        "credential in a known token format",
    ),
    LineRule(
        "credential",
        re.compile(
            r"(?i)(?:key|token|secret|password|passwd)[\"']?\s*[:=]\s*"
            # Unquoted values exclude brackets, so code such as key = value.strip() passes.
            r"(?:[\"'][^\"'\s]{16,}[\"']|[^\s\"'#,;()\[\]{}]{16,})"
        ),
        "secret-looking assignment",
        _placeholder_ok,
    ),
    LineRule(
        "email",
        re.compile(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
        ),
        "email address; the only public contact is support@metix.ai",
        _email_ok,
    ),
    LineRule(
        "phone",
        re.compile(
            r"(?<![\w.])\+\d[\d\s().-]{7,}\d(?![\w.])|\(\d{3}\)\s?\d{3}[-.\s]\d{4}\b"
            r"|\b\d{3}[-.]\d{3}[-.]\d{4}\b"
        ),
        "phone number",
        _phone_ok,
    ),
    LineRule(
        "profile-url",
        re.compile(r"(?i)linkedin\.com/(?:in|pub)/|xing\.com/profile/"),
        "link to a personal profile",
    ),
    LineRule(
        "local-path",
        re.compile(
            r"/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|\b[A-Za-z]:\\Users\\"
        ),
        "local home-directory path",
    ),
    LineRule(
        "private-ip",
        re.compile(
            r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"
        ),
        "private network address",
    ),
    # The product is always "Metix AI Platform". The shorter forms name the company
    # and the main site at metix.ai, and this repository belongs to neither.
    LineRule("brand", re.compile(r"\bMETIX\b"), "write Metix AI Platform"),
    LineRule(
        "brand", re.compile(r"\bMetix\b(?! AI Platform\b)"), "write Metix AI Platform"
    ),
    LineRule(
        "brand", re.compile(r"\bMetixAI\b(?!-Official)"), "write Metix AI Platform"
    ),
    LineRule(
        "brand",
        re.compile(r"\bOpenJobs\b(?! AI Inc)"),
        "OpenJobs appears only as OpenJobs AI Inc. in legal text",  # check-public: allow brand
    ),
    LineRule(
        "dash",
        re.compile("[\u2013\u2014]"),
        "em or en dash; use a period, comma, colon, or parentheses",
    ),
)


def load_denylist(
    env: Mapping[str, str] | None = None, root: Path | None = None
) -> list[str]:
    """Read internal terms from the environment and the local ignored file."""
    env = os.environ if env is None else env
    raw = env.get(DENYLIST_ENV, "").replace(",", "\n").splitlines()
    path = (ROOT if root is None else root) / DENYLIST_FILE
    if path.is_file():
        raw += path.read_text(encoding="utf-8").splitlines()
    terms = {line.strip() for line in raw}
    return sorted(t for t in terms if len(t) >= 3 and not t.startswith("#"))


def compile_denylist(terms: Iterable[str]) -> re.Pattern[str] | None:
    terms = sorted(set(terms), key=len, reverse=True)
    if not terms:
        return None
    body = "|".join(re.escape(t) for t in terms)
    return re.compile(rf"(?<![A-Za-z0-9])(?:{body})(?![A-Za-z0-9])", re.IGNORECASE)


def _allowed_rules(line: str) -> set[str]:
    match = PRAGMA.search(line)
    if not match:
        return set()
    return {name.strip() for name in match.group(1).split(",")}


def check_lines(
    path: str, text: str, denylist: re.Pattern[str] | None
) -> list[Finding]:
    in_data = bool(DATA_PATH.match(path))
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        allowed = set() if in_data else _allowed_rules(line)
        seen: set[str] = set()
        for rule in LINE_RULES:
            if rule.name in allowed or rule.name in seen:
                continue
            for match in rule.pattern.finditer(line):
                if rule.accept and rule.accept(match.group(0)):
                    continue
                findings.append(Finding(path, number, rule.name, rule.message))
                seen.add(rule.name)
                break
        if denylist and "denylist" not in allowed and denylist.search(line):
            findings.append(
                Finding(
                    path, number, "denylist", "internal term from the private denylist"
                )
            )
    return findings


def _is_count_key(key: str) -> bool:
    return key in {"count", "n"} or key.endswith("_count")


def _is_person_key(key: str) -> bool:
    # names, profile_urls, photos: an array of records is still record-level.
    singular = key[:-1] if key.lower().endswith("s") else key
    return bool(PERSON_KEY.match(key) or PERSON_KEY.match(singular))


def _as_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)?", value.strip()):
        return float(value)
    return None


def _profile_cells(
    node: object, limit: int, where: str = "", key: str = ""
) -> Iterator[Finding]:
    """Small cells, and numbers under keys the small-cell rule cannot see.

    The findings carry no file path; check_data adds it.
    """
    if isinstance(node, dict):
        for child, value in node.items():
            here = f"{where}.{child}" if where else str(child)
            yield from _profile_cells(value, limit, here, str(child))
    elif isinstance(node, list):
        # Elements inherit the list's key, so "count": [3, 120] is checked too.
        for index, value in enumerate(node):
            yield from _profile_cells(value, limit, f"{where}[{index}]", key)
    elif _is_count_key(key):
        number = _as_number(node)
        if number is not None and 0 < number < limit:
            message = f'{where} counts fewer than {limit} people; write "<{limit}"'
            yield Finding("", None, "small-cell", message)
    elif (
        isinstance(node, (int, float))
        and not isinstance(node, bool)
        and not NUMERIC_KEY.search(key)
    ):
        # Fail closed: a count stored as "visible" or "total" would skip the rule.
        message = (
            f"{where} is a number under a key that is not a count, share, "
            "or statistic; name counts count, n, or *_count"
        )
        yield Finding("", None, "data-format", message)


def check_data(path: str, text: str) -> list[Finding]:
    """Rules for committed aggregates under cases/<slug>/data/."""
    name = path.rsplit("/", 1)[-1]
    if RAW_PATH.match(path):
        return [
            Finding(
                path,
                None,
                "data-format",
                "raw records never leave data/raw/, which git ignores",
            )
        ]
    if name.startswith("."):
        return []
    if not name.endswith(".json"):
        return [
            Finding(
                path,
                None,
                "data-format",
                "aggregates are JSON files with a declared unit",
            )
        ]

    findings = [
        Finding(path, number, "person-field", "person-level field in published data")
        for number, line in enumerate(text.splitlines(), start=1)
        for key in JSON_KEY.findall(line)
        if _is_person_key(key)
    ]
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        return [*findings, Finding(path, None, "data-format", "not valid JSON")]
    if name == "receipt.json":
        return findings
    if not isinstance(doc, dict) or doc.get("unit") not in UNITS:
        unit_list = ", ".join(sorted(UNITS))
        return [
            *findings,
            Finding(path, None, "data-format", f"missing unit ({unit_list})"),
        ]
    if doc["unit"] == "profiles":
        declared = doc.get("min_cell")
        limit = (
            max(MIN_CELL, declared)
            if isinstance(declared, int) and not isinstance(declared, bool)
            else MIN_CELL
        )
        findings += [
            Finding(path, None, cell.rule, cell.message)
            for cell in _profile_cells(doc, limit)
        ]
    return findings


def check_file(
    path: str, data: bytes, denylist: re.Pattern[str] | None
) -> list[Finding]:
    """All findings for one file, given its repository-relative path and content."""
    if b"\x00" in data[:8192]:
        return []
    text = data.decode("utf-8", errors="replace")
    findings = check_lines(path, text, denylist)
    if DATA_PATH.match(path):
        findings += check_data(path, text)
    return findings


def _git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True
    ).stdout


def _split_z(output: bytes) -> list[str]:
    return [p for p in output.decode("utf-8").split("\0") if p]


def iter_sources(paths: list[str], staged: bool) -> Iterator[tuple[str, bytes]]:
    if paths:
        for raw in paths:
            path = Path(raw).resolve()
            try:
                rel = path.relative_to(ROOT).as_posix()
            except ValueError:
                rel = raw
            yield rel, path.read_bytes()
        return
    if staged:
        for rel in _split_z(
            _git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR")
        ):
            yield rel, _git("show", f":{rel}")
        return
    for rel in _split_z(
        _git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    ):
        path = ROOT / rel
        if path.is_file():
            yield rel, path.read_bytes()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check files against the public data policy."
    )
    parser.add_argument(
        "paths", nargs="*", help="files to check (default: the repository)"
    )
    parser.add_argument(
        "--staged", action="store_true", help="check only staged content"
    )
    args = parser.parse_args(argv)

    denylist = compile_denylist(load_denylist())
    findings: list[Finding] = []
    scanned = 0
    for rel, data in iter_sources(args.paths, args.staged):
        scanned += 1
        findings += check_file(rel, data, denylist)

    for finding in findings:
        print(finding.format())
    files = len({f.path for f in findings})
    if findings:
        print(
            f"check_public: {len(findings)} findings in {files} of {scanned} files",
            file=sys.stderr,
        )
        print("See docs/public-data-policy.md.", file=sys.stderr)
        return 1
    print(f"check_public: {scanned} files clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
