# Metix AI Platform use cases

Questions about the job market answered with data from the [Metix AI Platform](https://platform.metix.ai): professional profiles, job postings, and companies behind one query API. Every use case publishes the queries behind its numbers and what those queries cost to run, so you can check the work and run it again on your own key.

The cases will also be published as a website on GitHub Pages, starting with the first finished case.

## Use cases

| Use case | Type | Data | Status |
| --- | --- | --- | --- |
| Coding-agent companies and who they hire | Study | People, jobs, companies | Planned |
| China-educated AI talent in industry | Study | People, companies | Planned |
| Inference as a P&L function | Study | People, jobs, companies | Planned |

Titles are working titles. A published case is titled with its finding.

The China-educated study defines its population by the country or region of each person's undergraduate institution, and by nothing else. It does not use names, languages, or any inferred ethnicity or nationality.

## Four kinds of use case

| Type | What you get |
| --- | --- |
| Study | A market question answered with people, jobs, and companies together, in 8 or more charts |
| Snapshot | One question and one chart, cheap enough to rerun on the free plan |
| Recipe | Runnable code for a task you want to automate, such as a watchlist or an alert |
| Agent session | A question put to an agent using [metix-skills](https://github.com/MetixAI-Official/metix-skills) or the MCP server, with every query it ran |

Each case shows the Query Spec behind every chart and a receipt for the whole run: calls, results, records, and Credits, taken from the Platform's own balance before and after the run.

## Rerun a case

Once a case is published, it runs on Python 3.10 or later with no packages to install:

```bash
export METIX_KEY=metix_xxxxxxxxxxxx
python3 cases/<slug>/fetch.py
```

Create a key at [platform.metix.ai/api-keys](https://platform.metix.ai/api-keys). The free plan starts with 100 Credits and needs no card. Copy `.env.example` to `.env` if you prefer a file; `.env` is ignored by git. Field names, operators, limits, and prices are defined by the live contract (`GET /contract`) and the [Platform docs](https://platform.metix.ai/docs); if a case and the contract disagree, the contract wins.

## How the repository is organized

```text
cases/<slug>/     one folder per use case: metadata, method, queries, fetch script, aggregates
cases/_template/  the folder to copy when starting a case
docs/             how the repository works and the rules every case follows
scripts/          the public data check and its tests
```

- [docs/framework.md](docs/framework.md): case types, the case folder contract, the data flow, and how the site is built.
- [docs/public-data-policy.md](docs/public-data-policy.md): what may be published and what may not.
- [docs/style.md](docs/style.md): brand, writing, design system, and chart rules.

## Public data rules

Only aggregates are published. No case names a person, links to a profile, or publishes a record, and any count of people below 10 is shown as `<10`. No case infers ethnicity, nationality, gender, or age, from names or from anything else. Counts of profiles are lower bounds, visible in the Metix AI index on the snapshot date, and never a company's headcount.

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
- [metix.ai/reports](https://metix.ai/reports/): published research reports from Metix AI, a separate library

## License

Code (the scripts, each case's `fetch.py`, and the site source) is licensed under the [Apache License 2.0](LICENSE). Written content, charts, and the published aggregates in `cases/*/data/` are licensed under [Creative Commons Attribution 4.0](LICENSE-CONTENT); credit Metix AI when you reuse them.

Copyright 2026 OpenJobs AI Inc. Metix AI is a product of OpenJobs AI Inc.
