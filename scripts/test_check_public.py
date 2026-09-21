"""Tests for check_public.

Every fake secret, address, and misspelling below is assembled at runtime, so
this file passes the checker it tests.
"""

from __future__ import annotations

import json

import check_public as cp
import pytest

FAKE_KEY = "metix_" + "0123456789abcdef" * 2
GMAIL = "jane.doe" + "@" + "gmail.com"
HOME = "/Users" + "/someone/notes.md"


def rules(path: str, text: str, denylist: list[str] | None = None) -> list[str]:
    pattern = cp.compile_denylist(denylist or [])
    return [f.rule for f in cp.check_file(path, text.encode(), pattern)]


def aggregate(unit: str, rows: list[dict], **extra: object) -> str:
    return json.dumps(
        {"unit": unit, "snapshot": "2026-09-18", "rows": rows, **extra}, indent=2
    )


@pytest.mark.parametrize(
    "text",
    [
        "Create a key at https://platform.metix.ai/api-keys.",
        "METIX_KEY=metix_xxxxxxxxxxxx",
        'export METIX_KEY="' + "metix_xxxxxxxxxxxx" + '"',
        '"credits_source": "GET /auth/key/status before and after the run"',
        "                key = value.strip().strip(quotes)",
        'Call metix_get_contract first, then send "Authorization: Bearer $METIX_KEY".',
        "Metix AI Platform, by Metix AI. Legal entity: " + "Open" + "Jobs AI Inc.",
        "git clone git@github.com:MetixAI-Official/awesome-metix-platform-use-cases.git",
        "Write to support@metix.ai. Example: someone@example.com.",
        "Visible profiles rose 12.5% to 3,041 on 2026-09-18T09:30:00+00:00.",
        "npx skills add MetixAI-Official/metix-skills",
    ],
)
def test_clean_text_passes(text: str) -> None:
    assert rules("docs/example.md", text) == []


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        (f"the leaked value was {FAKE_KEY}", "key"),
        ("mira_" + "a" * 32, "key"),
        ("token = " + '"' + "q" * 20 + '"', "credential"),
        ("AWS_SECRET_KEY=" + "Z" * 20, "credential"),
        ('"key": "' + "k" * 20 + '"', "credential"),
        ("gh" + "p_" + "A" * 36, "credential"),
        (f"Contact {GMAIL}", "email"),
        ("Call +1 (415) 555-" + "0134", "phone"),
        ("https://www.linkedin.com" + "/in/" + "someone", "profile-url"),
        (f"see {HOME}", "local-path"),
        ("host 192." + "168.1.20", "private-ip"),
        ("MET" + "IX data", "brand"),
        ("Met" + "ix platform", "brand"),
        ("Met" + "ixAI platform", "brand"),
        ("Open" + "Jobs data", "brand"),
        ("a pause " + chr(0x2014) + " then", "dash"),
        ("pages 3" + chr(0x2013) + "5", "dash"),
    ],
)
def test_line_rules_fire(text: str, rule: str) -> None:
    assert rules("docs/example.md", text) == [rule]


def test_findings_never_print_the_match(tmp_path, capsys) -> None:
    leaked = tmp_path / "notes.md"
    leaked.write_text(f"key: {FAKE_KEY}\nmail: {GMAIL}\n", encoding="utf-8")

    assert cp.main([str(leaked)]) == 1

    out = capsys.readouterr()
    printed = out.out + out.err
    assert FAKE_KEY not in printed
    assert GMAIL not in printed
    assert ":1: key:" in printed and ":2: email:" in printed


def test_pragma_allows_only_the_named_rule() -> None:
    line = "Never write " + "MET" + "IX. <!-- check-public: allow brand -->"
    assert rules("docs/style.md", line) == []
    assert rules("docs/style.md", line + f" {GMAIL}") == ["email"]


def test_pragma_is_ignored_in_data_files() -> None:
    text = (
        aggregate("jobs", [{"group": "MET" + "IX", "count": 3}])
        + "  # check-public: allow brand"
    )
    assert "brand" in rules("cases/demo/data/jobs.json", text)


def test_denylist_matches_whole_terms_and_is_not_printed(
    tmp_path, capsys, monkeypatch
) -> None:
    term = "quokka" + "ingest"
    assert rules("docs/a.md", f"built on {term.upper()} v2", [term]) == ["denylist"]
    assert rules("docs/a.md", f"built on {term}er", [term]) == []

    monkeypatch.setenv(cp.DENYLIST_ENV, f"{term}\n# comment\nab")
    monkeypatch.setattr(cp, "ROOT", tmp_path)
    assert cp.load_denylist() == [term]

    note = tmp_path / "a.md"
    note.write_text(f"uses {term}\n", encoding="utf-8")
    assert cp.main([str(note)]) == 1
    out = capsys.readouterr()
    assert term not in out.out + out.err


def test_denylist_file_is_read(tmp_path) -> None:
    (tmp_path / cp.DENYLIST_FILE).write_text(
        "alpha-host.internal\n\n", encoding="utf-8"
    )
    assert cp.load_denylist(env={}, root=tmp_path) == ["alpha-host.internal"]


def test_small_profile_cells_are_flagged_with_their_path() -> None:
    text = aggregate(
        "profiles",
        [
            {"group": "Serving", "count": 120},
            {"group": "Kernels", "count": 7},
            {"group": "Evals", "count": "<10"},
        ],
    )
    findings = cp.check_file("cases/demo/data/staff.json", text.encode(), None)
    assert [(f.rule, f.message.split()[0]) for f in findings] == [
        ("small-cell", "rows[1].count")
    ]


def test_small_cell_checks_nested_keys_and_numeric_strings() -> None:
    text = aggregate(
        "profiles", [{"group": "A", "by_year": {"2025": {"hire_count": "4"}}}]
    )
    assert rules("cases/demo/data/flow.json", text) == ["small-cell"]


def test_declared_min_cell_can_raise_but_not_lower_the_floor() -> None:
    rows = [{"group": "A", "n": 12}]
    assert rules(
        "cases/demo/data/a.json", aggregate("profiles", rows, min_cell=20)
    ) == ["small-cell"]
    assert rules(
        "cases/demo/data/a.json", aggregate("profiles", [{"n": 5}], min_cell=3)
    ) == ["small-cell"]


def test_unrecognized_numeric_keys_fail_closed() -> None:
    for row in ({"group": "Kernels", "visible": 3}, {"group": "Kernels", "total": 300}):
        assert rules("cases/demo/data/a.json", aggregate("profiles", [row])) == [
            "data-format"
        ]


def test_shares_statistics_and_dimensions_are_allowed() -> None:
    row = {
        "group": "A",
        "year": 2025,
        "rank": 1,
        "count": 120,
        "share": 0.42,
        "median_tenure_months": 38,
        "salary_p75": 210000,
    }
    assert (
        rules("cases/demo/data/a.json", aggregate("profiles", [row], min_cell=10)) == []
    )


def test_list_elements_inherit_the_count_key() -> None:
    text = aggregate("profiles", [{"group": "A", "count": [120, 3]}])
    assert rules("cases/demo/data/a.json", text) == ["small-cell"]


def test_zero_and_job_counts_are_not_small_cells() -> None:
    assert (
        rules(
            "cases/demo/data/a.json",
            aggregate("profiles", [{"group": "A", "count": 0}]),
        )
        == []
    )
    assert (
        rules("cases/demo/data/b.json", aggregate("jobs", [{"group": "A", "count": 2}]))
        == []
    )


@pytest.mark.parametrize(
    "key",
    [
        "full_name",
        "name",
        "names",
        "linkedinUrl",
        "linkedinUrls",
        "email",
        "profile_id",
        "profile_urls",
        "photo_url",
        "photos",
    ],
)
def test_person_fields_in_data_are_flagged(key: str) -> None:
    text = aggregate("jobs", [{key: "x", "count": 40}])
    assert "person-field" in rules("cases/demo/data/rows.json", text)


def test_data_files_need_json_and_a_unit() -> None:
    assert rules("cases/demo/data/rows.csv", "group,count\nA,40\n") == ["data-format"]
    assert rules("cases/demo/data/a.json", json.dumps({"rows": []})) == ["data-format"]
    assert rules("cases/demo/data/a.json", "{not json") == ["data-format"]
    assert rules("cases/demo/data/raw/records.json", "[]") == ["data-format"]
    assert rules("cases/demo/data/.gitkeep", "") == []


def test_receipt_needs_no_unit() -> None:
    receipt = {
        "ran_at": "2026-09-18T09:30:00Z",
        "calls": 3,
        "results": 75,
        "records": 0,
        "credits": 3,
    }
    assert rules("cases/demo/data/receipt.json", json.dumps(receipt)) == []


def test_data_rules_apply_only_under_cases_data() -> None:
    text = aggregate("profiles", [{"name": "A", "count": 3}])
    assert rules("docs/example.json", text) == []


def test_binary_files_are_skipped() -> None:
    assert (
        cp.check_file(
            "site/public/fonts/sora.woff2", b"wOF2\x00\x01" + FAKE_KEY.encode(), None
        )
        == []
    )
