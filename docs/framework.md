# Framework

How the repository is organized, what a use case contains, how numbers get from the API to the page, and how the site is built. The data rules live in `docs/public-data-policy.md` and the visual and writing rules in `docs/style.md`.

## Who this is for

The reader is a developer or analyst deciding whether the Metix AI Platform can answer their questions. They arrive from platform.metix.ai, from GitHub, or from a link to a single case. They want to see a real question answered with the data, check how each number was produced, and run it again on their own key.

That sets the one principle every case follows: each number on the page shows the query that produced it and what that query cost in Credits. The published reports at [metix.ai/reports](https://metix.ai/reports/) present conclusions and keep query mechanics out of view. This repository does the opposite, because here the mechanics are what the reader came to evaluate. The prose still leads with the finding.

## Use case types

The catalog mixes four types so it shows the range of what the Platform does, not only long reports. No single type should make up more than half of the published cases.

| Type | What it is | Shape | What the reader does next |
| --- | --- | --- | --- |
| Study | A market question answered with people, jobs, and companies together | 6 to 10 numbered sections, 8 or more charts | Reads the finding, opens a query, reruns one section |
| Snapshot | One question, one chart | Under 300 words, cheap enough to rerun on the free plan | Copies the query and changes one filter |
| Recipe | A task a developer wants to automate, such as a watchlist, an enrichment, or an alert | Runnable code, expected output shape, cost per run | Runs it on a schedule |
| Agent session | A question put to an agent that uses metix-skills or the MCP server | The prompt, the queries the agent ran, and the answer, with no raw records | Installs the skills and asks their own question |

### First cases

The three planned studies:

1. Coding-agent companies and who they hire: companies that sell a coding agent, including people whose titles never say "Agent".
2. China-educated AI talent: industry stock and return versus stay, with the population defined by where the undergraduate institution is. See the sensitive-attribute rules in the data policy before starting this one.
3. Inference as a P&L function: inference and serving providers, and serving teams inside frontier labs.

Each study should also produce at least one smaller case from the same queries, so the catalog grows in several types at once. Candidates, to be confirmed against real data:

- Snapshot: where inference roles are posted, by metro.
- Recipe: a weekly watchlist of companies that open post-training roles.
- Agent session: asking an agent with metix-skills which coding-agent companies hire outside the US.

## Repository layout

```text
.
├── README.md
├── LICENSE                     Apache-2.0, for code
├── LICENSE-CONTENT             CC BY 4.0, for text, charts, and aggregates
├── docs/
│   ├── framework.md            this file
│   ├── public-data-policy.md   what may and may not be published
│   └── style.md                brand, voice, design system, chart rules
├── cases/
│   ├── _template/              copy this folder to start a case (never built)
│   └── <slug>/                 one folder per use case
├── scripts/
│   ├── check_public.py         leak and small-cell check
│   └── test_check_public.py
├── site/                       Astro site, added with the first case
└── .github/workflows/
    └── public-check.yml        runs the check on every push and pull request
```

`site/` and the Pages workflow arrive with the first case, so the site is designed against real content rather than placeholders.

## The case contract

```text
cases/<slug>/
├── case.yaml       metadata the site and the checks read
├── README.md       question, definitions, method, limits, how to rerun
├── index.mdx       the page body (story and charts), added once the site exists
├── queries/        one Query Spec tree per JSON file, named for what it counts
├── fetch.py        runs the queries with METIX_KEY and writes data/
└── data/
    ├── *.json      aggregates, the only data the page may read
    ├── receipt.json
    └── raw/        records needed during computation; ignored by git
```

The slug is lowercase words joined by hyphens. Studies and snapshots end with the snapshot year (`inference-pnl-2026`) because their numbers describe a point in time; recipes and agent sessions do not.

`README.md` is what someone browsing GitHub reads, and the site renders it as the "Method and limits" section of the case page, so method text is written once.

### `case.yaml`

| Field | Values | Notes |
| --- | --- | --- |
| `slug` | string | Matches the folder name |
| `title` | string | The finding, in sentence case, at most 90 characters. Until the data exists, a working title marked in `status: draft` |
| `dek` | string | One sentence: scope, population, and period |
| `type` | `study`, `snapshot`, `recipe`, `agent` | |
| `status` | `draft`, `published` | Drafts do not build. They are still public once pushed |
| `datasets` | any of `people`, `jobs`, `companies` | |
| `integration` | any of `rest`, `mcp`, `skills` | How the case calls the Platform |
| `topics` | list of short slugs | For catalog filters, for example `ai-talent`, `inference` |
| `regions` | list of ISO country codes or `global` | |
| `snapshot` | date | The day the queries ran |
| `published` | date or empty | Set when `status` becomes `published` |

The site validates this file at build time and fails on any missing or unknown field.

### Aggregate files

Every file the page reads from `data/` has the same outer shape, so the checker and the chart components can rely on it:

```json
{
  "unit": "profiles",
  "snapshot": "2026-09-18",
  "query": "queries/visible-inference-staff.json",
  "min_cell": 10,
  "rows": [
    { "group": "Serving", "count": 120 },
    { "group": "Kernels", "count": "<10" }
  ]
}
```

`unit` is `profiles`, `jobs`, or `companies`. Counts sit under a key named `count`, `n`, or ending in `_count`. For `profiles`, cells from 1 to 9 are written as the string `"<10"` by `fetch.py`, before anything reaches `data/`. The numbers above show the shape only.

Aggregates are JSON; the checker rejects any other format under `data/`. Row labels use keys such as `group`, `company`, or `label`, never `name`, because the checker treats `name` and other person-level keys (contact fields, profile links, person ids), singular or plural, as a leak.

In a `profiles` file, every number must sit under a count key, a share or ratio (`share`, `pct`, `ratio`, or a key ending in one of them), a statistic (`mean`, `median`, `p75`, or a key starting or ending with one), or a numeric dimension (`year`, `month`, `quarter`, `rank`). The checker rejects a number under any other key, because a count stored as `visible` or `total` would otherwise skip the small-cell rule.

### The receipt

`fetch.py` writes `data/receipt.json` at the end of every run:

```json
{
  "ran_at": "2026-09-18T09:30:00Z",
  "calls": 0,
  "results": 0,
  "records": 0,
  "credits": 0,
  "credits_source": "GET /auth/key/status before and after the run"
}
```

Credits are the remaining balance reported by `GET /auth/key/status` before the run minus the balance after it. That route is free, so the receipt costs nothing, and the number is the Platform's own accounting rather than an estimate. Run cases with a key that nothing else uses at the same time, or the difference includes unrelated calls. Nobody edits a receipt by hand.

## From query to page

```text
queries/*.json ──> fetch.py ──> data/raw/        (records, never committed)
                      │
                      └──────> data/*.json       (aggregates, small cells suppressed)
                               data/receipt.json
                                      │
                                      v
                          site build: case.yaml + index.mdx + README.md
                                      │
                                      v
                          GitHub Pages (static HTML, charts as SVG)
```

`fetch.py` uses the Python standard library only, reads `METIX_KEY` from the environment, and never prints it. It prefers queries whose result totals answer the question and pulls records only when the case needs a field that no filter can express. Every Search response carries a `total`, exact below a threshold and a banded string above it (the threshold is on `GET /contract`), so a chart built from totals must handle the banded form rather than assume an integer. Suppression happens inside `fetch.py`, so no unsuppressed number is ever written to a tracked path.

A shared client (authentication, paging, the receipt, suppression) will live in `tools/` once a second case needs the same code. Until then each case keeps its own small `fetch.py`.

## The site

### Stack

The site is built with [Astro](https://astro.build) as static HTML and deployed to GitHub Pages by an Actions workflow. Astro is what metix.ai is built with, so tokens and fonts carry over; its content collections validate `case.yaml` at build time, which turns the case contract into a build error instead of a review comment; and it ships no JavaScript unless a component asks for it.

The alternative was plain HTML files with a small Python script to generate the catalog. It needs no Node toolchain, but every page would carry its own copy of the header, footer, and styles, and those copies drift. With more than a handful of cases, a shared layout is what keeps the catalog looking like one product.

Charts are Astro components that read an aggregate file and render SVG at build time. The reader downloads finished SVG, not a charting library. A chart becomes interactive only when interaction answers a question the static version cannot.

### Pages

| Path | Content |
| --- | --- |
| `/` | The catalog: every published case, filterable by type and dataset |
| `/cases/<slug>/` | One case |
| `/method/` | Definitions shared by every case: visible lower bound, snapshot date, small-cell rule, how Credits are counted |

Global navigation stays the same on every page: the Metix AI Platform mark (to `/`), Use cases, Method, Docs (platform.metix.ai/docs), GitHub, and one primary action, Get an API key (platform.metix.ai/api-keys).

### Address

The default address is `https://metixai-official.github.io/awesome-metix-platform-use-cases/`, so the Astro `base` is the repository name. A custom domain later only changes `base` and a `CNAME` file.

## Checks

| Check | Where | Fails on |
| --- | --- | --- |
| `scripts/check_public.py` | pre-commit hook, CI | Leaks and small cells, see the data policy |
| `case.yaml` schema | site build | Missing or unknown fields, wrong enum values |
| Case completeness | site build | A published case without `receipt.json`, or a chart reading a file that does not exist |
| Visual check | before publishing | Pages not rendered and checked at 1440 and 375 pixels wide, see `docs/style.md` |

Run the leak check before every commit:

```bash
python3 scripts/check_public.py            # every tracked and untracked file
python3 scripts/check_public.py --staged   # only what is about to be committed
```

## Branches and publishing

Work happens on `feature/<YYYYMMDD>_<slug>` or `fix/<YYYYMMDD>_<slug>` branches and merges into `main` with a plain merge. `main` is what the site deploys. A pushed branch is public even before it merges, so a case is pushed only after it passes the leak check.

## Open decisions

1. Address. Keep the github.io address or move to a custom domain.
2. Languages. English only for now; metix.ai reports are bilingual.

Licensing is settled: code under Apache-2.0 (`LICENSE`), written content, charts, and published aggregates under CC BY 4.0 (`LICENSE-CONTENT`).
