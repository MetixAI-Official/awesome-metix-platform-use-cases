# Working title until the data exists

One sentence with the scope, the population, and the period.

The site renders this file as the "Method and limits" section of the case page. Replace every paragraph below, and delete this one.

## Question

What this case answers, in one or two sentences, and who would ask it.

## Population and definitions

Which people, jobs, or companies are counted, with the filters written out in words. Define every group that a chart uses. A population defined by education or work location says which location it uses; see "Sensitive attributes and their proxies" in `docs/public-data-policy.md`.

## Method

Which queries run (one file each in `queries/`), what each one counts, and how the aggregates in `data/` are built from them. Say which numbers come from Search totals and which from records, and how small cells were suppressed.

## Limits

What the data cannot show here. Counts of profiles are lower bounds: they cover what is visible through the Metix AI Platform on the snapshot date, not a company's headcount.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/replace-with-slug-2026/fetch.py
```

The last run's calls, results, records, and Credits are in `data/receipt.json`.

## Also in this folder

`PROMPT.md` and `PROMPT.zh.md` hold the bootstrap prompt; start from the skeleton here. The report page goes in `report/Report.astro`; `cases/inference-roles-us-metros-2026/report/Report.astro` is a working example of the component contract (`lang`, `section`, `entry`) and of the design note it opens with.
