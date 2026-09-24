# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 2,400 到 2,800 Credits：计数约 2,000，为挑选和核对而做的搜索与记录读取约 240（最大的公司、它们员工的一个切片、小团队大额融资的公司），核对环节 150 到 450（定义切片、主题切片、增长字段检查）。超过 3,000 之前它会先停下来问你。发布的每个公司数字都是计数，人员数字也是计数，读取记录只用于挑选和核对。

```text
用 Metix AI Platform 回答一个问题：ChatGPT 于 2022-11-30 发布；此后几年里成立了多少家自述为 AI 公司的企业？它们在哪里，说自己做什么，长到了多大，融资情况如何，员工之前在哪里工作？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），所有条件只用 querySpecByEntity.company 和 querySpecByEntity.profile 里的字段；再读 GET /docs/api/companies 和 GET /docs/api/query-spec（免费）。keywords、name、industry、headquarters.city 都是自由文本：match 和 eq 都表示每个词都出现、顺序不限、不分大小写，in 表示多个这样的值任取其一。size 只取九个固定值。总数达到 100,000 时返回的是字符串 "100000+"。一次查询最多 64 个条件。size 1 的计数花 1 Credit，搜索每返回 25 个 ID 花 1 Credit，读取详情每 5 条记录花 1 Credit。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 3,000 Credits 之前先停下来问我。

2. 范围。AI 公司指：type 不是 Nonprofit、Educational 或 Government Agency，并且满足以下之一：名称里有 AI 这个词，且 keywords 匹配 AI、artificial intelligence、generative AI、machine learning、large language models、LLM、deep learning、computer vision、natural language processing 中任意一个；或者 keywords 匹配 deep learning、computer vision、natural language processing、large language models、generative AI 中任意一个。按 founded_year（只有年份）分组：2019 到 2022 年（之前；发布日是 2022-11-30，所以 2022 年算作之前），2023 到 2025 年（这一届），以及 2026 年至今。把定义和分组写进文件。

3. 先核对定义，再做任何测量。搜索结果按匹配程度排序，所以绝不能凭搜索结果的前几条判断一个定义。要读完整的切片：某个成立年份里、linkedin_followers 落在一个窄区间内的全部匹配公司，每片 15 到 50 家，2016 到 2025 年每年一片（共约 200 家；_source 取 id、name、industry、keywords、type、founded_year）。逐家手工分类：AI 就是产品；AI 是另一领域核心产品的一部分；在众多服务里顺带列出 AI 的综合型公司；与 AI 无关或根本不是公司。前两类算 AI 公司。按成立时期报告比例。再用同样的切片方式读定义排除掉的、九个宽松词的匹配公司，报告其中有多少是 AI 公司。预期分别约为 78% 和约三分之一：标签是随意写的，综合型公司也爱列 AI 词，只看名称又会偏向新公司。如实报告，不要为了凑数把规则调到贴合这批样本。

4. 成立潮。2010 到 2026 年每个成立年份，数 AI 公司和全部公司。全部公司的总数大多数年份会被分段显示：按 size 的各档和无 size 拆开，某一档仍被分段就再按 headcount 拆（0、1、2、3 到 4、5 到 10、11 及以上、无），各部分相加。发布 AI 公司占当年成立的全部公司的比例；最近几年的记录都不全，这个比例不受影响。同时对每个分支和更宽、更窄的定义算同样的比例：只看名称分支；只看技术标签分支；技术分支只用 deep learning、computer vision、natural language processing（命名风气和 2022 年后的新词都影响不到它）；探测时的四个词；九个宽松词。只陈述在各口径下都成立的结论。展示这种滞后：按 updated_at 月份和是否有 headcount，统计每个成立年份的 AI 公司数。

5. 在哪里。对这一届和 2019 到 2022 年两组：约 60 个候选国家各数一次 headquarters.country，取前 15 名，加上其余和无国家，合计等于该组总数。都市圈用一个国家、一个城市列表（放在一个 in 条件里），以及一个要么写明、要么缺失的州（这一届旧金山的 891 家公司里有 165 家没有州）；新加坡取整个国家。每个比例都同时给出占全组的比例和占写明城市（或国家）的公司的比例，并在探测词和宽松词口径下重算湾区、旧金山市和伦敦。按成立年份统计总部在中国的全部公司数，说明这部分覆盖有多薄。

6. 做什么。2016 到 2026 年每个成立年份，统计 keywords 匹配以下 15 个主题的 AI 公司所占比例：generative AI；LLM；AI agents 或 agentic；computer vision；NLP；machine learning；robotics（不含 robotic process automation）；data analytics；SaaS；health；fintech；cybersecurity；developer tools；语音；AI 基础设施（GPU、inference、MLOps）。每个主题读一个小切片，去掉那些靠不同标签里的词拼出来的词（financial technology、information security、AI infrastructure），以及主要标出服务公司的词（devops）。再在宽松词人群里（任一宽松词，同样排除这三类 type）算同样的主题比例，避免名称分支不带标签进来造成某个主题下降。

7. 规模、增长、融资。每个成立年份的 size 分档。headcount_growth_yoy_pct 分六档加未写明，只统计 headcount 11 及以上的公司，这一届对比 2019 到 2022 年；先读 30 条记录，确认数值是百分比。每组有 last_funding.date、有 last_funding.amount 的比例（只是最近一轮）。2023Q1 到 2026Q3 每季度的最近一轮融资数。金额分档只统计总部在美国的公司：别的国家金额用的是本币（一个 8 人的韩国团队显示 23,000,000,000）。然后读取 2022 年及以后成立、headcount 50 及以下、最近一轮 50,000,000 及以上的全部美国 AI 公司，剔除融资日期早于成立年份的、这种团队却有十亿美元级融资的，以及 AI 只是众多标签之一的公司。对同样类型的全部公司（不加 AI 条件）也算增长分档、融资覆盖、美国金额分档和规模分档，以便区分 AI 公司的特点和年轻公司的共性。按季度的融资图画到 2026Q1 为止：记录在 2026 年 4、5 月刷新。

8. 员工。读取这一届 headcount 60 及以上的 AI 公司，取最大的 150 家；2016 到 2019 年的取 headcount 200 及以上，同样取 150 家。按名称数每家公司的在职资料（has_experience 里 experience.company.name eq 公司名，且 experience.is_current eq true）；在职人数超过 headcount 1.5 倍的名称剔除，不是公司的部门、实验室、社群也剔除。对剩下的每家公司按第 3 步的分类手工判断，只保留 AI 公司；把员工多为外包标注人员的数据标注平台单列一类，每个员工数字都给出含和不含这一类的两个版本。对保留公司的员工读一个完整切片（total_experience_months 落在一个窄区间），带上 experience.company.id，剔除大多数资料指向其他公司 id 的名称。然后统计目前在任一保留公司工作、且之前在以下雇主有过非实习经历的人数：Google、DeepMind、Meta、OpenAI、Anthropic、Microsoft、Amazon、Apple、NVIDIA、Stripe、Uber、Airbnb、Salesforce、Palantir、Databricks，以及 Scale AI（2016 到 2019 年这一组不统计，因为 Scale AI 本身就在组里）；再统计任一大型科技公司、任一前沿实验室的合计；以及 current_title 匹配 founder 的人数。

9. 输出和图表。聚合文件带 "unit"（公司为 companies，员工为 profiles）、快照日期和来源查询文件。人员数据：1 到 9 写成 "<10"，分母不少于 30 才发布比例，合计与其已显示成员相差 1 到 9 时不发布该合计。图表：按成立年份的 AI 占比，标出不完整的年份；两组的主要国家和都市圈；各主题比例按年份做小多图；增长分档；按季度的融资；小团队列表做成表格；之前雇主与基准组对比。每张图的标题用中性、客观的措辞写出结论。

10. 局限。这是一个精确的核心，不是普查：定义大约只保留四成 AI 公司，匹配到的公司里约五分之一并不是 AI 公司。发布之后的增幅有多大，取决于公司怎么描述自己：按名称和新词大约是三倍，按旧的技术标签只多约五分之一；计数分不清是做 AI 的公司变多了，还是说自己做 AI 的公司变多了。founded_year 只有年份，记录在 2026 年 4、5 月刷新，所以 2025 年不完整，2026 年只覆盖几个月。last_funding 只是一轮，美国以外的金额是本币，headcount 是公司主页上报的数字。员工数是可见资料，靠名称关联，绝不是人数规模。
```

## 怎么改成你自己的问题

| 要改什么 | 改哪里 | 例子 |
| --- | --- | --- |
| 什么算 AI 公司 | 第 2 步，然后在第 3 步重新核对 | 把 machine learning 加进技术词，预期准确率会下降 |
| 从哪次发布算起 | 第 2 步的分组 | 从 GPT-4（2023-03-14）算起需要月份，而 founded_year 没有月份 |
| 国家 | 第 4 到 8 步的 headquarters.country | 只看英国公司，都市圈用伦敦和剑桥 |
| 雇主 | 第 8 步的名单 | 加上 xAI、Mistral AI 或字节跳动 |
| Credit 上限 | 第 1 步和第 8 步 | 跳过员工关联（第 8 步），可省约 530 Credits |

## 运行前先问清楚

有人带着更模糊的问题来时，先把这几点定下来。每一点都会改变查询或花费：

1. 什么样的公司算 AI 公司：看名称、看标签，还是都看？能接受多少噪音？
2. 平台只存成立年份，哪几年算发布之后？
3. 看哪些国家？不同币种的金额还要不要放在一起比？
4. 要不要做员工关联？用哪一组做基准？
