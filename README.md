# Metix AI Platform use cases

Job-market reports made by an AI agent on the [Metix AI Platform](https://platform.metix.ai): professional profiles, job postings, and companies behind one query API. Every report publishes the queries behind its numbers, what those queries cost in Credits, and the prompt that produced it, so you can check the work, run it again on your own key, and change it to answer your own question.

The cases are published as **Casebook** at [metixai-official.github.io/awesome-metix-platform-use-cases](https://metixai-official.github.io/awesome-metix-platform-use-cases/), in English and in [Chinese](https://metixai-official.github.io/awesome-metix-platform-use-cases/zh/).

## Use cases

Reports are long reads with many figures. Cards are one question, one number, one chart.

| Use case | Format | Data | Credits to rerun |
| --- | --- | --- | --- |
| [Software and AI postings have the narrowest entry door of twelve US occupation families](cases/entry-level-postings-by-occupation-2026/) | Report | Jobs | 126 |
| [23.9% of US-based AI staff at ten labs who list a bachelor's earned it in mainland China](cases/china-educated-ai-talent-2026/) | Report | People | 104 |
| [Job postings ask for Claude Code five times as often as profiles list it](cases/ai-tool-stack-in-hiring-2026/) | Report | Jobs, people | 92 |
| [Claude Code is named in more job postings than any other AI coding tool](cases/ai-coding-tools-in-postings-2026/) | Card | Jobs | 14 |
| [Nearly half of US inference openings are in the Bay Area](cases/inference-roles-us-metros-2026/) | Card | Jobs | 96 |
| [Job titles name inference eight times as often as pre-training](cases/model-lifecycle-titles-2026/) | Card | Jobs | 8 |
| [Nearly two in three forward-deployed engineering openings are in the US](cases/forward-deployed-engineers-2026/) | Card | Jobs | 13 |
| [Half of US inference roles that state pay start between $150k and $200k](cases/us-inference-pay-2026/) | Card | Jobs | 6 |

Planned: coding-agent companies and who they hire, China-educated AI talent in industry, and inference as a P&L function. Their titles are working titles; a published case is titled with its finding. The China-educated study will define its population by the country or region of each person's undergraduate institution and by nothing else, never by names, languages, or any inferred ethnicity or nationality.

## How a case is made

An agent answers the question through the public Platform only: the REST API, the MCP server, or the [metix-skills](https://github.com/MetixAI-Official/metix-skills), with a normal Platform key. No internal data source is involved, so anyone with a key can reproduce any number here.

Each case keeps three things:

- **The prompt** (`PROMPT.md`, `PROMPT.zh.md`): one bootstrap prompt precise enough that an agent reproduces the case from it, with a table of the parameters you are most likely to change and the questions to settle before spending Credits.
- **The replay** (`queries/`, `fetch.py`): the queries the agent settled on, and a standard-library script that reruns them without an agent.
- **The receipt** (`data/receipt.json`): what the replay cost, taken from the Platform's own balance before and after the run.

## Four kinds of use case

| Type | What you get |
| --- | --- |
| Study | A market question answered with people, jobs, and companies together, in 8 or more charts |
| Snapshot | One question and one chart, cheap enough to rerun on the free plan |
| Recipe | Runnable code for a task you want to automate, such as a watchlist or an alert |
| Agent session | A conversation with an agent, published as the prompt, every query it ran, and the answer |

## Rerun a case

With an agent: open the case's `PROMPT.md`, copy the prompt, and paste it into an agent with Platform access.

Without one, on Python 3.10 or later with nothing to install:

```bash
export METIX_KEY=metix_xxxxxxxxxxxx
python3 cases/inference-roles-us-metros-2026/fetch.py
```

Create a key at [platform.metix.ai/api-keys](https://platform.metix.ai/api-keys). The free plan starts with 100 Credits and needs no card. You can also put `METIX_KEY` in a `.env` file at the repository root; git ignores it. Field names, operators, limits, and prices are defined by the live contract (`GET /contract`) and the [Platform docs](https://platform.metix.ai/docs); if a case and the contract disagree, the contract wins.

## How the repository is organized

```text
cases/<slug>/     one folder per use case: metadata, prompt, queries, replay, aggregates, report page
cases/_template/  the folder to copy when starting a case
tools/            the Platform client every fetch.py uses
site/             the Astro site (Casebook) that renders the catalog and every case, in English and Chinese
docs/             how the repository works and the rules every case follows
scripts/          the public data check and its tests
```

- [docs/framework.md](docs/framework.md): case types, the bootstrap prompt, the case contract, the data flow, and the site.
- [docs/public-data-policy.md](docs/public-data-policy.md): what may be published and what may not.
- [docs/style.md](docs/style.md): brand, writing, the site shell, per-report design, and chart rules.

To work on the site:

```bash
cd site
pnpm install
pnpm dev
```

## Public data rules

Only aggregates are published. No case names a person, links to a profile, or publishes a record, and any count of people below 10 is shown as `<10`. No case infers ethnicity, nationality, gender, or age, from names or from anything else. Counts of profiles are lower bounds, visible on the Metix AI Platform on the snapshot date, and never a company's headcount.

If you think something in this repository identifies a person or should not be public, email support@metix.ai rather than opening an issue, so the details are not repeated in public.

## Contributing

Proposals for new use cases are welcome as issues. Before any commit, run the public data check, which also runs in CI:

```bash
python3 scripts/check_public.py
```

To run it on every commit, install it as a hook:

```bash
printf '#!/bin/sh\nexec python3 scripts/check_public.py --staged\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Related

- [Metix AI Platform](https://platform.metix.ai) and its [docs](https://platform.metix.ai/docs)
- [metix-skills](https://github.com/MetixAI-Official/metix-skills): agent skills for the same API
- [metix.ai/reports](https://metix.ai/reports/): the research reports published on metix.ai

## License

Code (the scripts, each case's `fetch.py`, and the site source) is licensed under the [Apache License 2.0](LICENSE). Written content, charts, and the published aggregates in `cases/*/data/` are licensed under [Creative Commons Attribution 4.0](LICENSE-CONTENT); credit Metix AI Platform when you reuse them.

Copyright 2026 OpenJobs AI Inc. Metix AI Platform is a product of OpenJobs AI Inc.
