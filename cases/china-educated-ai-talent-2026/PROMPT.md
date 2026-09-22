# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. Followed end to end, it costs about 235 to 265 Credits: 104 for the published counts, about 120 to build and audit the institution list, and 10 to 40 for the name, location, and exclude-word checks. It stops and asks before 300. Every published number is a count; the reads only build and check the list.

```text
Answer one question with the Metix AI Platform: at ten large AI labs, what share of the people in AI roles earned their bachelor's degree at an institution in mainland China, and where do people in AI roles with that background list themselves now? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and build every condition from querySpecByEntity.profile. Conditions about one job go inside one has_experience entry and conditions about one degree inside one has_education entry, so they describe the same job or degree. A query holds at most 64 conditions and nests at most 6 levels deep. A count with size 1 costs 1 Credit, so plan every published number as a count. Check the balance with GET /auth/key/status (free) at the start and at the end, and stop and ask before the run passes 300 Credits.

2. Population. An AI role is a current job (experience.is_current eq true) whose experience.title matches any of: machine learning, research scientist, research engineer, deep learning, member of technical staff, applied scientist, artificial intelligence, AI engineer, AI researcher, LLM, NLP, computer vision. The labs, in this order, are OpenAI, Anthropic, Google DeepMind (company names "Google DeepMind" and "DeepMind"), xAI, Meta, NVIDIA, Google, Microsoft, Apple, and Amazon (with "Amazon Web Services (AWS)" and "AWS"). Check every name and variant with a count first. The Platform matches company names word by word, so Google also matches Google DeepMind. Make the rows disjoint: each lab counts people with a current AI role there and no current job at a lab earlier in the order, so the ten-lab figure is the sum of the rows.

3. The education rule. A person counts when one education entry has education.degree eq "Bachelor" and an institution located in mainland China. Decide by the institution and never by the person: no names, no languages. The denominator is people with any Bachelor entry. Mainland campuses of foreign and Hong Kong universities count; the list leaves out institutions in Hong Kong, Macau, and Taiwan.

4. Build the institution list. The school's country comes back on a detail read but cannot be queried, and it is missing for many mainland institutions. Search 250 profiles with a current AI role located in China (size 250), read them with POST /entity/v1/profiles/detail-by-id and _source on the education fields, and decide each Bachelor institution's location from its name. The Platform matches school names word by word, both match terms and names inside in, so a longer name that contains a listed one also matches. Write match terms only mainland institutions use (cities, provinces, distinctive names such as Tsinghua or Fudan), list other names in full, and add exclude words, in a not inside the same has_education entry, for names elsewhere that contain a listed one (National Sun Yat-sen University in Taiwan contains Sun Yat-sen University; Southeast Missouri State contains Southeast University). Check each exclude word with a count. Stay within the 64 conditions.

5. Audit the list. Read 25 AI-role profiles from each lab (250 in all), and check how many mainland Bachelor entries the list catches and whether it matches any institution outside mainland China. Fix the list and check again. Report the sample size and the result, and say that less common institutions can still slip through.

6. Location. Compare how often the job-level experience.location.country and the profile's location.country are filled for these people. Use the better covered one for "US-based", keep worldwide numbers as context, and say why.

7. Count. For each lab, disjoint as in step 2, US-based: AI roles; with any Bachelor entry; with a mainland-China Bachelor entry; the same two for current jobs that started in the last 24 months (experience.start_date gte "now-24m" in the same entry); the same two for titles that also match "scientist" or "researcher". Add the ten-lab figures as sums, but give no ten-lab total for a column with a suppressed cell. For context, the ten labs worldwide (one query with every name). Then twelve large institutions one at a time at the ten labs, US-based; a name that also matches other universities gets exclude words and is marked a strict count. Then where people in AI roles with a mainland-China Bachelor list themselves, by profile country. Every count of people goes through the small-cell rule (1 to 9 becomes "<10"), and before writing, check every count a reader could get by subtracting published cells; if one is between 1 and 9, suppress more and check again.

8. Outputs. Write labs.json, institutions.json, countries.json, and context.json with "unit": "profiles", the snapshot date, and the query files they came from, and commit the institution list with how it was built and audited. Raw records stay in data/raw/ and are never published.

9. Charts. The share by lab, US-based, sorted, with the ten-lab share marked; people whose current job started earlier against the last 24 months, for each lab; scientist and researcher titles against the same lab's other AI titles; the twelve institutions as counts, strict counts hatched; countries and regions other than mainland China scaled to the total. Every chart title states its finding in neutral, factual words. A bound keeps its direction when rounded: a floor rounds down, a ceiling rounds up.

10. Limits. Counts are visible lower bounds, not headcounts; shares are ratios within visible profiles that list a bachelor's and can sit above or below the share among all staff. People with no Bachelor entry are left out of both sides of every share. Profile location is where a person lists themselves, not always where the job is. Almost no profile lists China as its country, and people whose current job is recorded in China mostly list another country, so the data cannot say how many work in China; say so, give the visible counts for employers based in China, and make no claim about how many work there. The earlier group holds only people still in their job, so a gap between the groups can reflect who stayed as well as who was hired. One day, not a trend. No security, loyalty, or nationality framing.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The organizations | Step 2, checking each name with a count | Frontier startups: Mistral AI, Cohere, Perplexity |
| The roles | The title terms in step 2 | Data engineering or chip design titles |
| The education rule | Steps 3 to 5 | Institutions in India, built and audited the same way |

## What to ask before running it

1. Which organizations, and does any name also match a parent company or a different company?
2. Which roles, in title words?
3. Which country's institutions, and do campuses abroad count?
4. US-based, worldwide, or both?
5. How many Credits may the list building and the audit spend on reads?
