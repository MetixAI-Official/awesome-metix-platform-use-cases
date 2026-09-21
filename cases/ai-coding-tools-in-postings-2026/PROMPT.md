# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. It reproduces this card for about 15 Credits, plus whatever the audit reads.

```text
Answer one question with the Metix AI Platform: which AI coding tools do job postings name, and how often? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and use only querySpecByEntity.job fields. A count with size 1 costs 1 Credit; a search that returns nothing is free.

2. Tools. Claude Code, Cursor, GitHub Copilot, Codex, and Windsurf, matched in the job description (field "description", operator match).

3. Watch for ordinary words. match needs every word present but not side by side. Claude Code and GitHub Copilot are safe by name. Cursor, Codex, and Windsurf are also ordinary words (a database cursor, the Codex Alimentarius, a water sport).

4. Audit before trusting. For each tool, read 40 to 60 descriptions and check whether the words around the name are about AI coding. If more than 5% are not, count that tool only when the same description names another AI coding tool, and audit the tightened version. Keep the plain-word count as well, so the reader sees how much the definition moves it.

5. Count. Each tool worldwide and with location.country eq "United States", the plain-word count for any tightened tool, and one count for postings naming any of the five. About 15 Credits.

6. Clean. Reposts are not collapsed; say so.

7. Group. One file of tool definitions, with the tightened ones marked as lower bounds.

8. Outputs. Write data/tools.json with "unit": "jobs", the snapshot date, each tool's count, US count, and plain-word count where there is one, and the any-tool count. Report the balance from GET /auth/key/status before and after as the cost.

9. Chart. One bar per tool, sorted, the leader highlighted, tightened tools hatched with an outline behind showing the plain-word count. Title it with the finding.

10. Limits. Naming a tool is not the same as requiring it; some descriptions only say what the team uses. Tightened tools are lower bounds. One day, not a trend.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The tools | Step 2, and audit each new one in step 4 | Add Gemini Code Assist or JetBrains AI |
| The market | Step 5 | Count by country, or restrict to one industry |
| The field | Step 2 | Search titles instead of descriptions for roles built around a tool |

## What to ask before running it

1. Which tools, and could any of their names mean something else?
2. Descriptions or titles?
3. Worldwide, or one country?
4. How many Credits may the audit spend reading descriptions?
