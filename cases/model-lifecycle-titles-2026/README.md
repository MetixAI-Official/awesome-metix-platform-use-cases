# Job titles name inference eight times as often as pre-training

Open postings whose title names a stage of the model lifecycle, worldwide and in the US, on the Metix AI Platform on September 21, 2026.

## Finding

Worldwide, 516 open postings name inference or model serving in the title, 8.2 times the 63 that name pre-training. Post-training has 175 and fine-tuning 47. Post-training is the most US-concentrated stage: 138 of its 175 postings (79%) are in the US, against 35 of 63 (56%) for pre-training.

## Population and definitions

Open job postings on September 21, 2026. Each stage is a set of title words: pre-training (pretraining, pre-training), post-training (post-training, posttraining), fine-tuning (fine-tuning, finetuning), and inference (inference, model serving, llm serving). Every stage also requires a machine-learning word in the title (research, engineer, scientist, llm, model, ai, ml, technical) and excludes sales, customer, teacher, trainer, doctoral, pharmacy, licensing, licensed, causal, and statistical. The conditions are in [`queries/`](queries/).

## Method

Eight counts: each stage worldwide and in the US, one Credit each. No posting is read in the replay. `fetch.py` writes `data/stages.json` and `data/receipt.json`.

## How it was made

An AI agent built this card through the public REST API. Its first pre-training query matched "Pre-licensed Training Provided" and "Pharmacy Technician in Training", because a match needs every word present but not side by side. It read all 72 pre-training titles, added the machine-learning requirement and the exclusions, applied them to all four stages, and read the titles again to check. It dropped "RLHF" from post-training after one staffing firm's repeated "RLHF Specialist" postings filled the first page. Exploration cost about 93 Credits; the replay costs 8.

## Limits

Titles only, so every count is a lower bound: many people at frontier labs hold generic titles such as "Member of Technical Staff". Reposts are not collapsed. Postings measure demand, not headcount, and this is one day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/model-lifecycle-titles-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
