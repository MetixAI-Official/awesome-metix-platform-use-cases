# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. It reproduces this case end to end, for about N Credits.

Replace every line in the block, keep the order, and keep each step concrete: exact terms, exact fields, exact numbers. The finished prompt is what the case is made from, so a reader who runs it should get the published numbers. See `cases/inference-roles-us-metros-2026/PROMPT.md` for a complete one.

```text
Answer one question with the Metix AI Platform: <the question, in one sentence>. Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. <GET /contract, which dataset's fields, and the Credits page.>
2. Population. <Exact filters, terms, and exclusions, and how they are composed.>
3. Count first. <Which totals, with size 1, and what each costs.>
4. Budget. <Balance before and after, when to read records, the Credit ceiling to stop at.>
5. Audit. <Which sample to read, what counts as off-topic, and the threshold that triggers a fix.>
6. Clean. <Duplicates and missing values, and how each is counted.>
7. Group. <Every group as an explicit definition written to a file, and the leftover buckets.>
8. Outputs. <Aggregate files with "unit", snapshot date, and source query; raw records stay in data/raw/.>
9. Chart. <Form, order, scale, direct labels, and a title that states the finding.>
10. Limits. <What the numbers do not show.>
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| <The parameter a reader is most likely to change> | <The step and the words to edit> | <A concrete alternative> |

## What to ask before running it

When someone brings a looser version of this question, settle these first. Each one changes the query or the cost:

1. <Question>
