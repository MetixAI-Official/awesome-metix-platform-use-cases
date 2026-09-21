# Claude Code is named in more job postings than any other AI coding tool

Open postings whose description names an AI coding tool, worldwide, on the Metix AI Platform on September 21, 2026.

## Finding

36,208 open postings name at least one of five AI coding tools in the job description. Claude Code appears in 27,679 of them (76%), Cursor in at least 15,676, GitHub Copilot in 12,790, Codex in at least 7,878, and Windsurf in at least 2,234. The US share differs by tool: 41% of the Claude Code postings are in the US, against 19% for Windsurf.

## Population and definitions

Open job postings on September 21, 2026 whose description names a tool. Claude Code and GitHub Copilot match by name. Cursor, Codex, and Windsurf count only when the same description names another AI coding tool, because the plain words have other meanings; their plain-word counts (17,681, 8,290, and 2,302) are kept in `data/tools.json`. The conditions are in [`queries/`](queries/).

## Method

Fourteen counts, one Credit each: each tool worldwide and in the US, the three plain words, and postings naming any of the five. No posting is read in the replay.

## How it was made

An AI agent built this card through the public REST API. It read 40 to 60 descriptions per tool and checked the words around each name. Claude Code and GitHub Copilot meant the tool in 40 of 40. The plain words held in 55 of 60 for Cursor, 55 of 60 for Codex, and 56 of 60 for Windsurf, past the 5% error line, so their condition was tightened; tightened, Cursor held in 60 of 60. Exploration cost about 152 Credits, most of it reading descriptions; the replay costs 14.

## Limits

Naming a tool is not the same as requiring it. Cursor, Codex, and Windsurf are lower bounds. Reposts are not collapsed. One day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/ai-coding-tools-in-postings-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
