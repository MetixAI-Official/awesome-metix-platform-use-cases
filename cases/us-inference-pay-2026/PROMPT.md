# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. It reproduces this card for 6 Credits.

```text
Answer one question with the Metix AI Platform: what do US inference roles post as their pay floor? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and read the salary rules: a comparison on salary.annual_min needs salary.currency pinned with eq in the same all node, and figures are annualized within one currency, not converted.

2. Population. US open postings whose title matches any of "inference", "model serving", or "llm serving", minus titles that match "causal" or "statistical", with salary.currency eq "USD" and salary.annual_min present.

3. Count the denominator too. Count the same title filter in the US without the salary conditions, so the reader knows what share of postings state pay at all.

4. Bands without reading records. Count postings with salary.annual_min gte 150000, 200000, 250000, and 300000. Each band is the difference between two neighboring counts. Six counts, six Credits.

5. Check. The bands must add up to the number that state pay; if they do not, stop and say so.

6. Clean. Reposts are not collapsed; say so.

7. Group. Under $150k, $150k to $200k, $200k to $250k, $250k to $300k, and $300k or more.

8. Outputs. Write data/bands.json with "unit": "jobs", the snapshot date, the count that states pay, the US total, and each band. Report the balance from GET /auth/key/status before and after as the cost.

9. Chart. Vertical columns in band order, the largest band highlighted, with the share of postings that state pay written next to the headline number. Title it with the finding.

10. Limits. The posted minimum is the bottom of the base range, without bonus or equity. Companies that publish pay may differ from those that do not. The set is small.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The role | Step 2 | Any title filter from another card |
| The currency and country | Steps 2 and 3 | GBP with the United Kingdom, EUR with Germany |
| The measure | Step 4 | salary.annual_max for the top of the range |

## What to ask before running it

1. Which roles, and which country and currency?
2. The bottom of the range, the top, or both?
3. Which band edges?
