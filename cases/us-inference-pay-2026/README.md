# Half of US inference roles that state pay start between $150k and $200k

US postings with inference or model serving in the title that state an annual salary in USD, by posted minimum, on the Metix AI Platform on September 21, 2026.

## Finding

Only 61 of the 386 US postings with this title filter state an annual salary in USD (16%). Of those 61, 31 have a posted minimum between $150k and $200k, 17 between $200k and $250k, 8 between $250k and $300k, 2 at $300k or more, and 3 below $150k.

## Population and definitions

US open postings on September 21, 2026 whose title matches "inference", "model serving", or "llm serving", excluding "causal" and "statistical", with salary.currency USD and salary.annual_min present. The title condition is the same as in the Bay Area card. The condition is in [`queries/us-inference-usd.json`](queries/us-inference-usd.json).

## Method

Six counts, one Credit each: postings that state pay, postings at or above $150k, $200k, $250k, and $300k, and the US total without the salary conditions. Each band is the difference between two neighboring counts, so no posting is read.

## How it was made

An AI agent built this card through the public REST API while exploring the inference questions; it spent about 11 Credits, including a first run it later replaced. The replay costs 6.

## Limits

The posted minimum is the bottom of the base range, without bonus or equity. Companies that publish pay may differ from those that do not, and the set is small. Reposts are not collapsed. One day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/us-inference-pay-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
