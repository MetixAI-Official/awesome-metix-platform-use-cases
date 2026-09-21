# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. Followed end to end, it costs about 245 to 320 Credits: about 95 for the counts and the rest for the audit reads. It stops and asks before 320. Every published number is a count; the reads are only for the audits.

```text
Answer one question with the Metix AI Platform: for the AI coding assistants and agent frameworks that employers name in job postings, how does demand compare with the people who list them as skills? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free). Postings use querySpecByEntity.job and match "description"; profiles use querySpecByEntity.profile and match "skills". A count with size 1 costs 1 Credit, so plan every number as a count. Check the balance with GET /auth/key/status (free) at the start and at the end, and stop and ask before the run passes 320 Credits.

2. Tools. Coding assistants: Claude Code, Cursor, GitHub Copilot, Codex, Windsurf. Agent frameworks and protocols: LangChain, LangGraph, LlamaIndex, CrewAI, AutoGen, DSPy, and the Model Context Protocol (match "model context protocol").

3. Audit every name before trusting it. match needs every word present but not side by side. Read 40 to 60 job descriptions per tool and check that the words around the name are about AI. Cursor, Codex, and Windsurf are also ordinary words; if more than 5% of their matches are off-topic, count them only when the same text names another AI coding tool, on both postings and profiles, and audit again.

4. Keep ambiguous tools out of the ratio. After tightening, count their profiles too. If a tightened tool has only a few hundred profiles, its ratio mostly measures the definition, so show it in the demand charts as a lower bound and leave it out of any demand-to-supply comparison.

5. Count. For every tool: postings and profiles, worldwide and with location.country eq "United States". Every count of people goes through the small-cell rule (under 10 becomes "<10").

6. Dimensions, all as counts. Pairs of coding assistants named in the same posting. Postings naming any assistant by country (the ten largest plus the rest) and by a selected list of industries (say it is not a ranking, and that a posting can list several). US pay floors for postings naming any assistant and, as a baseline, for titles matching "software engineer": salary.currency eq "USD", then salary.annual_min gte 100000, 150000, 200000, 250000.

7. Beware of definitions that force the answer. A tool defined as "named alongside another tool" will always co-occur with another tool, so draw co-mention rows only for tools matched by name.

8. Outputs. Write demand.json and co-mentions.json, countries.json, industries.json, and pay.json with "unit": "jobs", supply.json with "unit": "profiles", each with the snapshot date and the query file it came from. Report the balance from GET /auth/key/status before and after as the cost.

9. Charts. A two-sided chart with profiles growing left and postings growing right on one scale; postings per profile on a log scale with a line at one to one; the same ratio split into the US and everywhere else; assistant counts with lower bounds hatched; the co-mention rows; countries scaled to the total; industries in two groups; pay as the share at or above each level for both groups. Every chart title states its finding.

10. Limits, stated before the first chart. Postings refresh daily but profile skills are self-reported and updated slowly, and the newest tools lag the most, so the ratio compares demand with published skills, not with the skills people have. Naming a tool is not the same as requiring it. Reposts are not collapsed. One day, not a trend.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The tools | Step 2, and audit each in step 3 | Vector databases: Pinecone, Weaviate, Qdrant, pgvector |
| The comparison | Step 6 | Replace the country split with seniority or job function |
| The market | Step 5 | Run it for one country: add its location.country to every count |

## What to ask before running it

1. Which tools, and could any name mean something else?
2. Demand only, or demand against supply? Supply needs profile skills and the small-cell rule.
3. Which breakdowns matter: countries, industries, pay?
4. How many Credits may the audits spend reading descriptions?
