# Job postings ask for Claude Code five times as often as profiles list it

Twelve AI coding assistants and agent frameworks, counted in open job postings and in profile skills on the Metix AI Platform on September 21, 2026.

## Findings

Of nine tools whose names cannot mean anything else, Claude Code has the widest gap between demand and supply: 27,679 open postings name it in the job description and 5,407 profiles list it as a skill, 5.1 postings per profile. LangChain runs the other way, with 30,546 profiles to 14,099 postings (0.46), and DSPy too (390 to 205). GitHub Copilot, LangGraph, and the Model Context Protocol sit near one to one.

The gap is wider outside the US. 64% of the profiles that list Claude Code are in the US, but only 41% of the postings that name it, so the ratio is 3.3 in the US and 8.4 everywhere else.

36,208 postings name at least one AI coding assistant. 55% of the postings that name GitHub Copilot also name Claude Code; only 25% of the Claude Code postings name Copilot. The US has 40% of these postings and India 10%. Financial services (4,092) outnumbers internet companies (3,101) among the industries checked.

Naming an assistant does not raise the posted pay floor in the US: 48% of such postings start at $150k or more, against 52% for software engineer titles.

## Population and definitions

Postings: open job postings on September 21, 2026 whose description names a tool. Profiles: profiles that list the same tool among their skills. Claude Code, GitHub Copilot, LangChain, LangGraph, LlamaIndex, CrewAI, AutoGen, DSPy, and the Model Context Protocol match by name. Cursor, Codex, and Windsurf count only when the same text names another AI coding tool, which leaves them 258, 452, and 13 profiles, so they stay out of the demand and supply comparison. Definitions: [`queries/tools.json`](queries/tools.json); countries, industries, and pay: [`queries/dimensions.json`](queries/dimensions.json).

## Method

92 counts, one Credit each. No posting and no profile is read. Every count of people passes the small-cell rule. `fetch.py` writes six aggregate files and the receipt to `data/`.

## How it was made

An AI agent built this report through the public REST API. It first checked each tool name against samples of job descriptions (Claude Code and GitHub Copilot 40 of 40, AutoGen 39 of 40; the plain words Cursor, Codex, and Windsurf 55 to 56 of 60, so they were tightened). It first pulled its industry list from the top of one search, saw that the list missed large industries, and replaced it with a wider list marked as selected rather than ranked. Two full runs were replaced along the way, one because the receipt counted free balance reads as calls. Exploration, those runs included, cost about 236 Credits; the replay costs 92.

## Limits

Profile skills are self-reported and updated slowly, and the newest tools lag the most, so the ratios compare demand with published skills rather than with the skills people have. Naming a tool is not the same as requiring it. Reposts are not collapsed. The pay groups overlap. One day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/ai-tool-stack-in-hiring-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
