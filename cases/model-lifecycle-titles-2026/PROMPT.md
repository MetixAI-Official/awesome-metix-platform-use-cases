# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. Followed end to end, it costs about 56 to 64 Credits: 8 for the counts and the rest for the audit reads. It stops and asks before 70.

```text
Answer one question with the Metix AI Platform: which stage of the model lifecycle do job titles name most often, and where is each stage hired? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and use only querySpecByEntity.job fields. A search costs ceil(returned IDs / 25) Credits, so a count with size 1 costs 1 Credit, and a search that returns nothing is free. Check the balance with GET /auth/key/status (free) at the start and at the end, and stop and ask before the run passes 70 Credits.

2. Stages. Four title conditions: pre-training (pretraining, pre-training), post-training (post-training, posttraining), fine-tuning (fine-tuning, finetuning), and inference (inference, model serving, llm serving). Use one any node per stage.

3. Guard every stage the same way. match needs every word present but not next to each other, so "pre-training" also matches "Pre-licensed Training Provided". Require one machine-learning word in the title (research, engineer, scientist, llm, model, ai, ml, technical) and exclude sales, customer, teacher, trainer, doctoral, pharmacy, licensing, licensed, causal, statistical. Do not add "RLHF" to post-training: data-labelling reposts from staffing firms dominate it.

4. Audit before trusting. Read every title for the smallest stage (it is under 100) and 50 titles for each of the others. Report how many are off-topic; if more than 5% are, add exclusions, apply them to all four stages, and say what changed.

5. Count. For each stage, count worldwide and with location.country eq "United States", size 1 each. Eight Credits in total.

6. Clean. Reposts are not collapsed here; say so rather than guessing a correction.

7. Group. The four stages are the groups; keep them in one file with their conditions.

8. Outputs. Write data/stages.json with "unit": "jobs", the snapshot date, and for each stage its worldwide count and US count. Report the balance from GET /auth/key/status (free) before and after as the cost.

9. Chart. One bar per stage, scaled to the largest, the inference bar highlighted, each labelled with its count and its US share. The headline number is the ratio of inference to pre-training, not a count.

10. Limits. Titles only: people at frontier labs often hold generic titles such as "Member of Technical Staff", so every count is a lower bound and the comparison is about how postings are titled, not about team size.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The stages | Step 2 | Add evaluation ("evals", "model evaluation") and audit it the same way |
| The guard | Step 3 | Tighten the machine-learning words for a noisier stage |
| The geography | Step 5 | Count by several countries instead of the US alone |

## What to ask before running it

1. Which stages, and which title words stand for each?
2. Titles only, or descriptions too? Descriptions are far noisier.
3. Worldwide, or one country?
4. How many Credits may the audit spend reading titles?
