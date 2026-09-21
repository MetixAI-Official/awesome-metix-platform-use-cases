# Nearly half of US inference openings are in the Bay Area

Open postings with inference or model serving in the title, grouped by US metro, as listed on the Metix AI Platform on September 21, 2026.

## Finding

Of 353 distinct US postings, 176 (49.9%) are in the San Francisco Bay Area. New York has 43 (12.2%) and Seattle 38 (10.8%); the Washington and Baltimore area, Boston, and Austin together have 36. Another 23 are elsewhere in the US, and 37 name no city.

120 companies posted these roles. The five with the most distinct postings are NVIDIA (44), Capital One (21), Anthropic (20), Amazon Web Services (19), and CoreWeave (14).

The US accounts for 386 of the 585 matching postings on the Platform worldwide, before reposts are collapsed.

## Population and definitions

Open job postings in the Platform's jobs index on September 21, 2026, whose title matches "inference", "model serving", or "llm serving", excluding titles that match "causal" or "statistical". The exclusions remove statistics roles ("causal inference"), which are not about serving models.

A distinct posting is one title, company, city, and state. A role reposted in the same city counts once; a role listed in three cities counts three times, once in each.

Metros are the city lists in [`metros.json`](metros.json). A city on no list counts as elsewhere in the US. A posting with no city, or with a state name in the city field, counts as no city given.

## Method

1. Count worldwide matching postings (`queries/world-total.json`, one Credit).
2. Search for US matching postings (`queries/us-postings.json`), then read each one's title, company, city, and state (`queries/us-postings-detail.json`, 100 per request).
3. Collapse same-city reposts, group by metro, and count companies.

`fetch.py` does all three and writes the results to `data/`.

## How it was made

An AI agent working through the public REST API built this case. Before writing the replay, it spent 111 Credits exploring: 7 on counts to size the question, and 104 to read every matching US posting once. That read found two things the queries now handle. First, 40 of 426 postings were statistics roles ("causal inference", "statistical"), so those terms are excluded. Second, 33 postings repeated a title, company, and city, so reposts are collapsed. It also showed how the index spells cities, and the metro lists were checked against those spellings. The published numbers come from one replay of the final queries, which cost 95 Credits.

## Limits

Postings measure demand, not headcount. A company that posts one role in several metros counts once in each. The index holds postings open on the snapshot day, and their posted dates are estimated, so this is a picture of one day, not a trend. Titles that describe inference work without using these words ("ML performance engineer", for example) are not counted, so the totals are a lower bound.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/inference-roles-us-metros-2026/fetch.py
```

It needs Python 3.10 or later and nothing else, and stops before reading records if the run would cost more than 150 Credits (`MAX_CREDITS`). The last run's cost is in [`data/receipt.json`](data/receipt.json). To make this case with an agent instead, use [`PROMPT.md`](PROMPT.md).
