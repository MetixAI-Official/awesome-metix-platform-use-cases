# Nearly two in three forward-deployed engineering openings are in the US

Open postings with forward deployed in the title, by country, on the Metix AI Platform on September 21, 2026.

## Finding

5,868 open postings worldwide have forward deployed in the title, and 3,801 of them (64.8%) are in the US. India is second with 309 (5.3%), then the United Kingdom (274) and Germany (241). Five European countries together have 691, about as many as every country outside the list of twelve (693).

## Population and definitions

Open job postings on September 21, 2026 whose title matches "forward deployed". The condition is in [`queries/forward-deployed.json`](queries/forward-deployed.json); the twelve countries are listed in `fetch.py`.

## Method

One worldwide count and one count per country, one Credit each. The rest of the world is the worldwide count minus the twelve. No posting is read in the replay.

## How it was made

An AI agent built this card through the public REST API. It read 500 postings to see which countries appear and took the twelve largest. Search results come in their own order, so that read was used only to choose countries: it put the US at 51%, while the full count says 64.8%. Exploration cost about 137 Credits, most of it that read; the replay costs 13.

## Limits

Titles only. A role listed in several cities or reposted counts more than once, so the numbers measure how loudly the title is advertised, not how many seats exist. One day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/forward-deployed-engineers-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
