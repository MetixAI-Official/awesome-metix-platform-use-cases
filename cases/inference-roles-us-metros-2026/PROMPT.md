# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. It reproduces this case end to end, for about 100 Credits.

```text
Answer one question with the Metix AI Platform: where in the United States are companies hiring for model inference right now? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and build every condition from querySpecByEntity.job. Read https://mira-api.metix.ai/docs/credits.md for prices: a search costs ceil(returned IDs / 25) Credits, a detail read costs ceil(found records / 5), and a search that returns nothing is free.
2. Population. Open job postings whose title matches any of "inference", "model serving", or "llm serving", minus titles that match "causal" or "statistical" (statistics roles, not model serving). Put the terms in one any node and the exclusions in one not node.
3. Count first. With size 1, record the worldwide total and the total with location.country eq "United States". Each count costs 1 Credit.
4. Budget. Call GET /auth/key/status (free) now and again at the end, and report the difference as the cost. If the US total is under 1,000, read every US posting: search with size 10000, then POST /entity/v1/jobs/detail-by-id in batches of 100 with _source ["title", "company.name", "location.city", "location.state"]. Stop and ask before anything that would take the run past 150 Credits.
5. Audit. List the 40 most common titles and flag any that are not about serving or optimizing models in production. If more than 5% of postings are off-topic, add exclusions to step 2, rerun, and say what you changed.
6. Clean. A posting with the same lowercased title, company, city, and state as an earlier one counts once. Report how many reposts this removed.
7. Group by metro: San Francisco Bay Area, New York, Seattle, Washington and Baltimore, Boston, and Austin, each an explicit list of city and state pairs written to metros.json. Check the lists against the cities you actually read, so no large suburb falls outside its metro. A city on no list counts as "elsewhere in the US"; a missing city, or a state name in the city field, counts as "no city given". Keep both buckets.
8. Outputs. Write data/metros.json (distinct postings and share by metro), data/companies.json (the five companies with the most distinct postings), and data/context.json (worldwide total, US total, records read, distinct postings), each with "unit": "jobs", the snapshot date, and the query file it came from. Keep the records in data/raw/ and never publish them.
9. Chart. One horizontal bar chart of distinct postings by metro, sorted by count, with "elsewhere" and "no city given" last and in grey. Scale the bars to each metro's share of all distinct US postings, not to the longest bar, and mark 50%. Label every bar with its count and share. Title the chart with the finding, not the topic.
10. Limits. Say what the numbers do not show: postings measure demand, not headcount; a role listed in several cities counts once per city; the index holds postings open on the snapshot day, and their posted dates are estimated.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The role | The title terms and exclusions in step 2, and the audit rule in step 5 | "post-training" or "reinforcement learning", excluding "sales" |
| The country | The country in step 3 and the metro lists in step 7 | United Kingdom, with London, Cambridge, and Edinburgh |
| The grouping | Step 7 and the chart in step 9 | Group by company instead of by metro |
| The budget | The ceiling in step 4 | 20 Credits: counts only, one count query per metro, no records |

## What to ask before running it

When someone brings a looser version of this question ("where are the inference jobs?"), settle these first. Each one changes the query or the cost:

1. Which roles, in title words, and what should be excluded?
2. Which geography, and at what level: country, state, or metro?
3. Which postings: everything open today, or only those posted in the last 30 or 90 days?
4. What to count: postings, distinct postings, or companies?
5. How many Credits the run may spend.
