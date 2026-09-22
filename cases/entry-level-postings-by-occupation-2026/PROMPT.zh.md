# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 211 到 261 Credits：发布用的计数 126，读取核对用的切片 75 到 105，确定切片大小和排除词的计数 10 到 30。超过 300 之前它会先停下来问你。发布的每个数字都是计数，读取只用于核对职位族。

```text
用 Metix AI Platform 回答一个问题：在美国仍在招聘的职位里，每个职业有多大比例的职位向刚入行的人开放？入门门槛窄，是软件和 AI 岗位独有的现象，还是研究认定 AI 暴露度较高的职业都一样？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），所有条件只用 querySpecByEntity.job 里的字段；再读 GET /docs/api/jobs（免费）。seniority 只取七个固定值之一（Associate、Director、Entry level、Executive、Internship、Mid-Senior level、Not Applicable），索引里每个职位的 is_open 都是 true，总数达到 100,000 时返回的是字符串 "100000+"。一次查询最多 64 个条件，嵌套最多 6 层。size 1 的计数花 1 Credit，搜索每返回 25 个 ID 花 1 Credit，读取详情每 5 个职位花 1 Credit，所以每个要发布的数字都按计数来设计。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 300 Credits 之前先停下来问我。

2. 范围。仍在招聘的职位（is_open eq true），且 location.country eq "United States"。按职位名称定义十二个职业族，每个族是一组职位名称词（title match：词组里的每个词都要出现，顺序不限）：AI 与机器学习（machine learning、artificial intelligence、AI、ML、LLM、deep learning；排除 data center、data centers）；软件工程（software engineer、software developer）；数据分析师（data analyst；排除 security、prevention）；财务分析师（financial analyst、finance analyst）；会计（accountant）；律师助理（paralegal、legal assistant）；平面设计（graphic designer、graphic design）；市场营销（marketing）；客户服务（customer service、customer support、customer care；排除 driver）；注册护士（registered nurse、RN）；电工（electrician）；卡车与 CDL 司机（truck driver、CDL driver）。在所有职业族之前，先拿掉 AI 训练和标注类工作：职位名称里有 AI 词，同时有 trainer、tutor、annotator、annotation 或 rater。每个职位只算一次：按上面的顺序，归入第一个匹配其职位名称词、又不匹配其排除词的族；匹配了排除词的职位继续交给后面的族判断。把职业族、顺序和每个排除词的理由写进文件。

3. 先核对再计数。搜索结果按职位名称的匹配程度排序，排在最前面的最干净，只看前几条会高估一个族的准确度。所以要读完整的切片：某个族在某一天（posted_date）、几个指定州里的全部职位，让一个切片有 10 到 50 条，每一条都读（POST /entity/v1/jobs/detail-by-id，_source 取 title、seniority、min_experience_months、company.name）。噪音多的族（AI、软件、数据分析师、财务分析师、市场营销、客户服务）各读约 40 条，其他族各读约 20 条。报告每个族切题的比例，说明噪音是什么，每个候选排除词都先用计数算出规模，只为读取中实际发现的噪音加排除词。读到的记录不能出现在任何公开文件里。

4. 两种口径。标签口径：seniority 为 Internship 或 Entry level 的职位，占该族全部职位的比例。每个职位都有 seniority，所以它是来源平台打的标签，不是雇主写明的要求。要求口径：min_experience_months lte 24（含 0）的职位，占写明 min_experience_months 的职位的比例；每个要求口径的比例旁边都要写出覆盖率，因为各族差别很大。任何时候都不按年龄定义入门。

5. 计数。每个族算：总数；seniority eq Internship、Entry level、Associate、Not Applicable，各一个计数；min_experience_months exists；min_experience_months lte 24；再把 seniority in [Internship, Entry level] 分别和后两个条件组合。先算所有族的总数。某个计数返回 "100000+" 时，把这个族拆成互不重叠的职位名称部分（registered nurse；有 RN 但没有 registered nurse）分别计数再相加。然后算核对中发现需要的四个子组：AI 训练类工作（总数和标签口径）；AI 族里职位名称还带软件族词的职位；industries 既不匹配 Retail 也不匹配 Restaurants 的客户服务职位；职位名称带 travel 的注册护士职位。每个族剩下的部分用减法得到。

6. 清理。计数的单位是职位帖子，不是空缺：同一个雇主在几个地方发同一个职位，就按帖子数算几次，所以要报告核对切片里有多少条和同一切片里另一条的职位名称、雇主都相同。没有 min_experience_months 的职位不在要求口径里，不能当成 0。

7. 比较。把写明经验要求的职位按两种口径分成四类（标为入门且要求 24 个月以内；标为入门但要求更多；未标为入门但要求 24 个月以内；两者都不是），报告两种口径在哪里不一致。报告标签口径里标为 Internship 的比例。AI 暴露度引用 Brynjolfsson、Chandar、Chen 的 "Canaries in the Coal Mine? Six Facts about the Recent Employment Effects of Artificial Intelligence"（Stanford Digital Economy Lab），只标注其在线附录表 A.2 到 A.6 给对应职业的五分位；这些表里没有对应职业的族不标，任何族都不给分数。

8. 输出。写出 families.json 和 subgroups.json，每个都带 "unit": "jobs"、快照日期和来源查询文件。分母不少于 30 才发布比例。核对时读到的记录不公开。

9. 图表。各族的标签口径比例，排序，标出每个族的 AI 暴露度五分位；旁边是要求口径比例和它的覆盖率；写明要求的职位按两种口径分成的四类；标签口径里实习的比例；带 AI 词和不带 AI 词的软件职位对比；旅行护士和其他护士职位对比。比例画在 0 到 100% 的坐标轴上，数值直接标在条上，每张图的标题用中性、客观的措辞写出结论。

10. 局限。这是某一天仍在招聘的职位，不是趋势，说不出门槛有没有变窄。职位帖子反映的是需求，不是录用；标签和写明的要求只代表帖子怎么写，不代表录用了谁。职位名称族只是近似论文里的职业，而且包含各个层级的岗位。各族写明经验要求的比例不同。要写清楚旅行护士和门店柜台岗位在多大程度上影响了护士和客户服务的数字。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 职业 | 第 2 步，新加的族都要按第 3 步核对 | 药剂师、教师或网页开发的职位名称 |
| 入门的口径 | 第 4 步 | 12 个月以内，或把 Associate 标签也算进来 |
| 国家 | 第 2 步的 location.country | United Kingdom，并换成当地的职位名称用词 |
| Credit 上限 | 第 1 步和第 3 步 | 不读核对切片，花费约 126 Credits |

## 运行前先问清楚

有人带着更笼统的问题来时，先把这几件事定下来，每一件都会改变查询或花费：

1. 看哪些职业？每个职业用职位名称里的哪些词？
2. 怎样才算向刚入行的人开放：来源平台的标签、写明的要求，还是两者都看？
3. 看哪个国家？
4. 核对读取最多能花多少 Credits？
