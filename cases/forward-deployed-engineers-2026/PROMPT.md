# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. Followed end to end, it costs about 130 to 145 Credits: 13 for the counts and the rest for the read that chooses the countries. It stops and asks before 150.

```text
Answer one question with the Metix AI Platform: in which countries are companies hiring forward-deployed engineers? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and use only querySpecByEntity.job fields. A count with size 1 costs 1 Credit. Check the balance with GET /auth/key/status (free) at the start and at the end, and stop and ask before the run passes 150 Credits.

2. Population. Open postings whose title matches "forward deployed". The phrase rarely means anything else; read 25 titles to confirm.

3. Count the whole population first. One worldwide count, size 1.

4. Find the countries. Read the country of about 500 postings to learn which countries appear. Search results come in their own order, not a random one, so this read only chooses the countries: never publish a share computed from it.

5. Count each country. For the twelve largest in that read, count with location.country eq the country name, size 1 each. The rest of the world is the worldwide count minus their sum.

6. Clean. Reposts and multi-city listings are not collapsed; say that the numbers measure how loudly the title is advertised, not how many seats exist.

7. Group. Twelve countries and the rest of the world, the list written into the script.

8. Outputs. Write data/countries.json with "unit": "jobs", the snapshot date, the worldwide count, and each country's count and share. Report the balance from GET /auth/key/status before and after as the cost.

9. Chart. One bar per country scaled to the worldwide total, the US highlighted, the rest of the world plain and last. Title it with the finding.

10. Limits. Titles only; the same work under another title (solutions engineer, for example) is not counted. One day, not a trend.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The role | Step 2 | "solutions engineer", "applied AI engineer", "AI deployment" |
| The breakdown | Steps 4 and 5 | Cities within one country, or a list of companies |
| The window | Step 2 | Add posted_date gte now-30d for recent postings only |

## What to ask before running it

1. Which title, and does it mean anything else?
2. Countries, cities, or companies?
3. Everything open, or only recent postings?
4. How many Credits may the discovery read spend?
