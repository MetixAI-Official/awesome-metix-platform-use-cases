# 23.9% of US-based AI staff at ten labs who list a bachelor's earned it in mainland China

AI roles at OpenAI, Anthropic, Google DeepMind, xAI, Meta, NVIDIA, Google, Microsoft, Apple, and Amazon, counted by where each person's bachelor's institution is located, on the Metix AI Platform on September 21, 2026.

## Findings

Across the ten labs, 19,178 US-based people in AI roles show a bachelor's degree on their profile, and 4,582 of them (23.9%) earned it at an institution in mainland China. Worldwide, not only in the US, the ten labs are at 19.0% (4,816 of 25,376).

The share ranges from 11.2% at Anthropic (73 of 652) to 36.0% at Meta (1,672 of 4,643). xAI (26.4%) is also above the ten-lab share, and Amazon (23.9%) is level with it; Google DeepMind, NVIDIA, Apple, OpenAI, Microsoft, and the rest of Google sit between 17% and 23%.

Among people whose current job started in the last 24 months, the share is 21.7% (1,975 of 9,089), against 25.8% among people whose current job started earlier. Lab by lab the gap is 2.6 points, and only Meta and Microsoft differ by more than chance: Meta 39.5% against 31.0%; Microsoft 20.8% against 14.8% (earlier against the last 24 months). The other labs differ within chance, in both directions. The earlier group has had longer to lose people who left, so the gap may reflect who stayed as well as who was hired.

In titles that name a scientist or researcher, the share is 32.2% (2,624 of 8,161) across the seven labs with enough such titles, against 17.9% for their other AI titles; at Meta it is 46.2%. Applied Scientist counts, and it covers most of Amazon's AI staff with a bachelor's. OpenAI, Anthropic, and xAI mostly use titles such as "Member of Technical Staff", so their scientist and researcher counts are too small to compare, and no ten-lab figure is published for this column.

Of the twelve named universities, Tsinghua University (520), Shanghai Jiao Tong University (409), University of Science and Technology of China (385), Zhejiang University (345), Peking University (332) lead; the twelve rows add up to 2,854 entries, and someone with bachelor's entries at two of them counts in both. Four rows are strict counts: the Platform matches names word by word, so, for example, the University of Science and Technology of China also matches the University of Electronic Science and Technology of China, and those rows leave out entries with the other university's words.

Across all employers, 15,802 people in AI roles hold a bachelor's from a mainland-China institution; 77.2% list the United States as their country, then Singapore (4.6%), Canada (3.7%), and the United Kingdom (2.5%). The Platform cannot say how many work in China (see Limits). Across all US-based AI roles with a bachelor's entry, more than 100,000, the 12,194 with a mainland-China bachelor's are at most 12.2%, so the ten labs' share is at least 1.9 times that of the wider US AI workforce.

## Population and definitions

An AI role is a current job whose title matches one of twelve AI terms, with the lab and any date condition in the same job entry. The lab rows do not overlap: someone with current jobs at two labs counts once, at the first in the list, so the ten-lab figures are sums of the rows. A person counts as having a mainland-China bachelor's when one Bachelor entry names an institution on [`queries/institutions.json`](queries/institutions.json): 37 match words that only mainland institutions use and 145 institution names, with 4 exclude words for names elsewhere that contain a listed one, decided by the institution and never by the person. Mainland campuses of foreign and Hong Kong universities count; the list is built to leave out institutions in Hong Kong, Macau, and Taiwan. Every share uses people with any Bachelor entry as its denominator (79.0% of the ten labs' US-based AI staff show one); against all visible staff the ten-lab figure is at least 18.9%. US-based uses the profile's location.country, which every profile in this population lists. Amazon includes Amazon Web Services. Definitions: [`queries/population.json`](queries/population.json).

## Method

105 counts, one Credit each (104 Credits for the reproduce run). No profile is read. Every count of people passes the small-cell rule, and `fetch.py` stops before writing if any count a reader could get by subtracting published cells is between 1 and 9. It writes four aggregate files and the receipt to `data/`.

## How it was made

An AI agent built this report through the public REST API. The school country recorded on an education entry cannot be queried and is missing for many mainland institutions (Beihang University and Huazhong University of Science and Technology among them), so the agent read 250 China-located AI profiles, decided each Bachelor institution's location from its name, and wrote the list. Two independent audits followed: 250 lab profiles (25 per lab), where the list caught all 28 mainland Bachelor entries, and 200 US-based profiles at Meta, Amazon, NVIDIA, and Microsoft, where it caught 60 of 63 and matched one institution in Taiwan. That second audit showed that the Platform matches names word by word, so the three missed institutions were added, exclude words were written, and four university rows became strict counts. A review of the first draft also found that per-lab worldwide counts and overlapping lab rows let a reader subtract their way to groups of fewer than 10 people; the rows are now disjoint and those columns are gone. Exploration cost about 203 Credits; the reproduce run costs 104.

## Limits

Counts are visible lower bounds, not headcounts. Shares are ratios within visible profiles that list a bachelor's, and can sit above or below the share among all staff; labs where more staff list a bachelor's also tend to have higher shares. People with no Bachelor entry are left out of both sides of every share. Less common institutions can slip through the list, so the shares are probably slightly low. Profile location is where a person lists themselves, not always where the job is. Almost no profile lists China as its country (32 AI-role profiles do), and people whose current job is recorded in China mostly list another country, so this data cannot say how many people with this background work in China. Employers based in China are thinly covered: on the Platform, ByteDance shows 498 visible profiles in AI roles, Tencent 92, Alibaba 74, Baidu 46, and DeepSeek fewer than 10. The start-date comparison does not account for job type. The title terms miss people whose title names no AI term. One day, not a trend.

## Rerun

```bash
export METIX_KEY=metix_xxxxxxxxxxxx   # create one at https://platform.metix.ai/api-keys
python3 cases/china-educated-ai-talent-2026/fetch.py
```

To make it with an agent instead, use [`PROMPT.md`](PROMPT.md).
