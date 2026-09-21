# Framework

How the repository is organized, what a use case contains, how numbers get from the Platform to the page, and how the site is built. The data rules live in `docs/public-data-policy.md` and the visual and writing rules in `docs/style.md`.

## What this is

A library of job-market reports, published as a website in English and Chinese, where every report was made by an AI agent working through the public Metix AI Platform. Each report does three things a reader can check:

1. States a finding, with charts built from committed aggregates.
2. Shows the queries behind every number and what rerunning them costs in Credits.
3. Ships the bootstrap prompt that produced it, so a reader can paste it into their own agent, run it on their own key, and change it to answer their own question.

Two readers matter. Someone who wants the finding reads the report. A developer or analyst deciding whether the Platform can answer their questions reads the prompt, the queries, and the receipt. The page serves the first reader first and keeps the second one a scroll away.

## Where the data comes from

Only from the public Metix AI Platform: the REST API at `https://mira-api.metix.ai`, the MCP server, or the metix-skills, with a normal Platform key. No internal database, export, or pipeline feeds any case. Anything in a report can be reproduced by anyone with a key, and a number that cannot be is a bug.

An agent does the work: it reads the live contract and docs, writes the queries, checks what comes back, and writes the case. What it learns while exploring (title noise, spelling of cities, duplicates) goes into the case's method, and the queries it settles on go into `queries/`. `fetch.py` then replays exactly those queries without an agent, so the published numbers come from one reproducible run.

## Use case types

| Type | What it is | Shape |
| --- | --- | --- |
| Study | A market question answered with people, jobs, and companies together | 6 to 10 numbered sections, 8 or more charts |
| Snapshot | One question, one chart | Short, and cheap enough to rerun on the free plan (100 Credits) |
| Recipe | A task a developer wants to automate, such as a watchlist or an alert | Runnable code, expected output shape, cost per run |
| Agent session | A conversation with an agent, published as the prompt, each call it made, and the answer | No raw records |

No single type should make up more than half of the published cases. Each study should also produce at least one smaller case from the same queries.

Types say what a case is; formats say how it is shown. A **card** is one question, one number, and one small chart, shown in the catalog as a field of color with a receipt stub; snapshots and most recipes are cards. A **report** is a long read with many figures, shown in the catalog as a full-width band; studies are reports. `docs/style.md` describes both.

## The bootstrap prompt

Every case ships `PROMPT.md` (and `PROMPT.zh.md`): one prompt, precise enough that an agent with Platform access reproduces the case from it. It is the case's source code in the sense that matters to a reader. It follows the same order every time, because that order is also what an agent should ask a user who arrives with a vague question:

1. **The question**, in one sentence.
2. **Access**: public Platform only, the key in `METIX_KEY`, never printed.
3. **Read first**: `GET /contract` and the Credits page, before building any query.
4. **Population**: the exact filters, the exclusions, and an audit step that reads a sample and reports how much of it is off-topic.
5. **Cost**: count with small pages first; read records only when the question needs a field no filter can express; a hard Credit ceiling; the balance before and after.
6. **Cleaning**: duplicates, missing values, and how each is counted.
7. **Grouping**: every group defined explicitly and written to a file.
8. **Outputs**: aggregates with a declared unit, the raw records kept private.
9. **Chart**: the form, the order, direct labels, a title that states the finding.
10. **Limits**: what the numbers do not show.

Below the prompt, an "Adapt it" table names the parameters a reader is most likely to change (role terms, geography, grouping, Credit ceiling) and the line each one lives on.

## Repository layout

```text
.
├── README.md
├── LICENSE                     Apache-2.0, for code
├── LICENSE-CONTENT             CC BY 4.0, for text, charts, and aggregates
├── docs/                       this file, the data policy, the style guide
├── cases/
│   ├── _template/              copy this folder to start a case (never built)
│   └── <slug>/                 one folder per use case
├── scripts/
│   ├── check_public.py         leak and small-cell check
│   └── test_check_public.py
├── tools/
│   └── metix_client.py         the Platform client every fetch.py uses
├── site/                       the Astro site (Casebook) that renders the catalog and every case
└── .github/workflows/
    ├── public-check.yml        runs the check on every push and pull request
    └── pages.yml               builds the site and deploys it to GitHub Pages from main
```

## The case contract

```text
cases/<slug>/
├── case.yaml             metadata the site reads and validates
├── README.md             question, definitions, method, limits, how to rerun (English, for GitHub readers)
├── PROMPT.md             the bootstrap prompt, and PROMPT.zh.md
├── queries/              one Query Spec per JSON file, named for what it asks
├── fetch.py              replays the queries with METIX_KEY and writes data/
├── <config>.json         any grouping the case defines, such as metros.json
├── data/
│   ├── *.json            aggregates, the only data the page reads
│   ├── receipt.json      what the last replay cost
│   └── raw/              records read during a run; ignored by git
└── report/
    └── Report.astro      the case's own page content, in both languages, with its own styles
```

The slug is lowercase words joined by hyphens. Studies and snapshots end with the snapshot year because their numbers describe a point in time; recipes and agent sessions do not.

### `case.yaml`

| Field | Values | Notes |
| --- | --- | --- |
| `slug` | string | Matches the folder name |
| `type` | `study`, `snapshot`, `recipe`, `agent` | |
| `format` | `card`, `report` | How the catalog and the page show it |
| `color` | `violet`, `blue`, `navy`, `teal`, `sky`, `periwinkle`, `signal` | A card's field color |
| `span` | `1`, `2` | Catalog columns a card takes; wide charts take two |
| `status` | `planned`, `draft`, `published` | Planned cases appear in the catalog as "Coming next", without a link. Drafts do not build. All three are public once pushed |
| `title` | `en`, `zh` | The finding, in sentence case, at most 90 characters. A working title until the data exists |
| `dek` | `en`, `zh` | One sentence: scope, population, and period |
| `datasets` | any of `people`, `jobs`, `companies` | |
| `integration` | any of `rest`, `mcp`, `skills` | How the agent called the Platform |
| `topics` | list of short slugs | |
| `regions` | list of ISO country codes, or `global` | |
| `snapshot` | date | The day the replay ran |
| `published` | date | Set when `status` becomes `published` |
| `exploration_credits` | number | Credits the agent spent exploring before the replay, runs it replaced included, so the full cost of making the case is on record |
| `highlights` | up to three `value` and `label` pairs | Figures shown on the catalog, copied from the case's aggregates |

The site validates this file at build time and fails on a missing or unknown field.

### Aggregate files

Every file the page reads from `data/` has the same outer shape, so the checker and the report components can rely on it:

```json
{
  "unit": "jobs",
  "snapshot": "2026-09-21",
  "query": "queries/us-postings.json",
  "rows": [
    { "group": "sf-bay-area", "count": 120, "share": 0.5 }
  ]
}
```

`unit` is `profiles`, `jobs`, or `companies`. Counts sit under a key named `count`, `n`, or ending in `_count`. For `profiles`, cells from 1 to 9 are written as the string `"<10"` by `fetch.py`, before anything reaches `data/`. The numbers above show the shape only.

Aggregates are JSON; the checker rejects any other format under `data/`. Row labels use keys such as `group`, `company`, or `label`, never `name`, because the checker treats `name` and other person-level keys, singular or plural, as a leak. Display labels in both languages live in the report, not in the data.

In a `profiles` file, every number must sit under a count key, a share or ratio (`share`, `pct`, `ratio`, or a key ending in one of them), a statistic (`mean`, `median`, `p75`, or a key starting or ending with one), or a numeric dimension (`year`, `month`, `quarter`, `rank`). The checker rejects a number under any other key, because a count stored as `visible` or `total` would otherwise skip the small-cell rule.

### The receipt

`fetch.py` writes `data/receipt.json` at the end of every run:

```json
{
  "ran_at": "2026-09-21T07:20:20Z",
  "calls": 8,
  "results": 387,
  "records": 386,
  "credits": 95,
  "credits_source": "GET /auth/key/status before and after the run"
}
```

Credits are the remaining balance reported by `GET /auth/key/status` before the run minus the balance after it. That route is free, and the number is the Platform's own accounting rather than an estimate. Only the balance is read from that response. Run cases with a key nothing else uses at the same time. Nobody edits a receipt by hand.

## From query to page

```text
agent explores the Platform  ─> queries/*.json, <config>.json, PROMPT.md
                                        │
                     fetch.py (replay) ─┼─> data/raw/            records, never committed
                                        └─> data/*.json          aggregates
                                            data/receipt.json
                                                   │
                     site build: case.yaml + report/Report.astro + data/ + PROMPT*.md
                                                   │
                                   GitHub Pages: /cases/<slug>/ and /zh/cases/<slug>/
```

`fetch.py` uses the Python standard library only, reads `METIX_KEY` from the environment or the repository's `.env`, never prints it, and stops before reading records if the run would pass its Credit ceiling. Every Search response carries a `total`, exact below a threshold and a banded string above it (the threshold is on `GET /contract`), so code built on totals must handle the banded form.

Every `fetch.py` uses `tools/metix_client.py`: it loads the key, counts with `size: 1`, pages a search after counting it first, reads records in batches of 100, applies the small-cell rule, and writes the receipt. It stops before any call whose worst case would take the run past its Credit ceiling, and it counts only search and detail calls, not the free balance reads.

## The site

Astro, built as static HTML and deployed to GitHub Pages from `main`. Astro is what metix.ai is built with; its content collections validate `case.yaml` at build time; and it ships no JavaScript unless a component asks for it. The only scripts on the page are the Copy buttons.

- `site/src/content.config.ts` loads every `cases/*/case.yaml` with the `glob()` loader and a schema.
- Routes: `/` and `/zh/` for the catalog; `/cases/<slug>/` and `/zh/cases/<slug>/` for reports. English is the default locale and has no prefix.
- Each case's `report/Report.astro` takes `lang`, `entry`, and a `section`: `card` (the card's number and mini chart, at `size` compact or full), `body` (the figures and findings; a report also renders its own hero here), and `method`. The shell calls each section where it belongs, so every case ends with the same three blocks in the same order. Shared components (`Figure`, `BarList`, the query disclosure, the prompt block, the receipt) come from `@site/components/`.
- The catalog order of cards is `CARD_ORDER` in `site/src/cases.ts`; wide cards lead their rows so the grid stays full.
- The default address is `https://metixai-official.github.io/awesome-metix-platform-use-cases/`, so the Astro `base` is the repository name. A custom domain later changes `base` and adds a `CNAME`.

Catalog filters and a method page arrive when the catalog is large enough to need them.

```bash
cd site
pnpm install
pnpm dev        # http://localhost:4321/awesome-metix-platform-use-cases/
pnpm build      # static output in site/dist/
```

## Checks

| Check | Where | Fails on |
| --- | --- | --- |
| `scripts/check_public.py` | pre-commit hook, CI | Leaks and small cells, see the data policy |
| `case.yaml` schema | site build | Missing or unknown fields, wrong enum values |
| Visual check | before publishing | Pages not rendered and checked at 1440 and 375 pixels wide, in both languages |

```bash
python3 scripts/check_public.py            # every tracked and untracked file
python3 scripts/check_public.py --staged   # only what is about to be committed
```

## Branches and publishing

Work happens on `feature/<YYYYMMDD>_<slug>` or `fix/<YYYYMMDD>_<slug>` branches and merges into `main` with a plain merge. `main` is what the site deploys. A pushed branch is public even before it merges, so a case is pushed only after it passes the leak check.

## Open decisions

1. Address: keep the github.io address or move to a custom domain.
2. How this library and metix.ai/reports relate once both exist: redirect, link, or migrate.

Licensing is settled: code under Apache-2.0 (`LICENSE`), written content, charts, and published aggregates under CC BY 4.0 (`LICENSE-CONTENT`).
