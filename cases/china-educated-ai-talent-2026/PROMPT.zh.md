# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 235 到 265 Credits：发布用的计数 104，建院校列表和核对约 120，公司名、地点和排除词的核对 10 到 40。超过 300 之前它会先停下来问你。发布的每个数字都是计数，读取只用于建列表和核对。

```text
用 Metix AI Platform 回答一个问题：十家大型 AI 机构里，从事 AI 岗位的人有多大比例本科就读于中国大陆院校？有这种背景的 AI 从业者现在的档案写在哪个国家或地区？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），所有条件只用 querySpecByEntity.profile 里的字段。同一份工作的条件放在同一个 has_experience 里，同一个学位的条件放在同一个 has_education 里，这样它们说的才是同一份工作、同一个学位。一次查询最多 64 个条件，嵌套最多 6 层。size 1 的计数花 1 Credit，所以每个要发布的数字都按计数来设计。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 300 Credits 之前先停下来问我。

2. 人群。AI 岗位指当前的一份工作（experience.is_current eq true），职位名称 experience.title 匹配以下任意一个：machine learning、research scientist、research engineer、deep learning、member of technical staff、applied scientist、artificial intelligence、AI engineer、AI researcher、LLM、NLP、computer vision。十家机构按这个顺序是 OpenAI、Anthropic、Google DeepMind（公司名 "Google DeepMind" 和 "DeepMind"）、xAI、Meta、NVIDIA、Google、Microsoft、Apple 和 Amazon（加上 "Amazon Web Services (AWS)" 和 "AWS"）。每个公司名和变体都先用计数核对。平台按词匹配公司名称，所以 Google 也会匹配到 Google DeepMind。各行要互不重叠：每家机构只算当前在这里做 AI 岗位、且当前不在顺序更靠前的机构任职的人，这样十家合计就是各行之和。

3. 学历口径。一条教育经历的 education.degree eq "Bachelor"，且院校位于中国大陆，这个人就计入。只看院校，不看人：不用姓名，不用语言。分母是有任意一条 Bachelor 经历的人。外国和香港高校在中国大陆设立的校区算大陆院校；清单不含香港、澳门、台湾的院校。

4. 建院校列表。院校所在国家在读取详情时会返回，但不能用来查询，而且很多大陆院校这一项是空的。搜索 250 个当前 AI 岗位在中国的档案（size 250），用 POST /entity/v1/profiles/detail-by-id 读取，_source 只取教育字段，按院校名称判断每所本科院校的所在地。平台对院校名称按词匹配，match 词和 in 里的名称都一样，所以含有清单名称全部用词的更长名称也会被匹配。match 词只用大陆院校名称才会出现的词（城市、省份，以及 Tsinghua、Fudan 这类独有的名字），其他名称写全称，再在同一个 has_education 里用 not 加上排除词，去掉含有清单名称但属于其他地方的院校（台湾的 National Sun Yat-sen University 含有 Sun Yat-sen University 的全部用词，Southeast Missouri State 含有 Southeast University）。每个排除词都用计数核对。总条件数控制在 64 以内。

5. 核对列表。从每家机构读 25 个 AI 岗位档案（共 250 个），看列表能抓到多少条大陆本科经历，有没有误匹配到大陆以外的院校。修改列表再核对。报告样本量和结果，并说明不常见的院校仍可能漏掉。

6. 地点。比较工作层面的 experience.location.country 和档案层面的 location.country 在这些人里各有多少人填写。"在美国"用覆盖更好的那个字段，全球数字作为背景，并说明理由。

7. 计数。每家机构按第 2 步互不重叠地分别算，都限在美国：AI 岗位人数；其中有任意 Bachelor 经历的；其中本科在中国大陆院校的；后两项在当前工作开始于最近 24 个月的人里的数字（同一份工作里加 experience.start_date gte "now-24m"）；后两项在职位名称同时匹配 "scientist" 或 "researcher" 的人里的数字。十家合计用各行之和，但只要某一列有被隐藏的格子，这一列就不给十家合计。再用一个列出所有公司名的查询算十家在全球的数字作为背景。然后在十家机构的美国 AI 员工里逐个数 12 所大学；名称还会匹配到其他大学的，加上排除词，并标为严格计数。最后看本科在中国大陆院校的 AI 从业者的档案写在哪个国家或地区。每个关于人的计数都要过小格子规则（1 到 9 写成 "<10"）；写出文件之前，检查读者能用已公开的格子相减得到的每一个数，只要有一个在 1 到 9 之间，就多隐藏一些再检查。

8. 输出。写出 labs.json、institutions.json、countries.json、context.json，每个都带 "unit": "profiles"、快照日期和来源查询文件；院校列表连同构建和核对过程一起提交。原始记录放在 data/raw/，永远不公开。

9. 图表。各机构在美国的比例，排序，并标出十家合计的比例；每家机构当前工作开始得更早的人和开始于最近 24 个月的人对比；职位名称含 scientist 或 researcher 的和同一机构其他 AI 职位对比；12 所大学的人数，严格计数用斜线条；中国大陆以外的各国家和地区按占总数的比例画。每张图的标题用中性、客观的措辞写结论。上下限取整时方向不变：下限向下取，上限向上取。

10. 局限。人数是可见的下限，不是在职人数；比例是可见且写了本科经历的档案内部的比例，可能高于也可能低于全部员工中的实际比例。没有 Bachelor 经历的人不进任何比例的分子或分母。档案里的国家是本人填写的所在地，不一定是工作地点。几乎没有档案把国家写成中国，当前工作记录在中国的人大多写的是别的国家，所以这些数据说不出有多少人在中国工作；要明确写出这一点，给出总部在中国的雇主的可见人数，也不对有多少人在中国工作做任何判断。更早的一组只包括仍在这份工作上的人，所以两组之间的差距反映的也可能是谁留下，而不只是招了谁。这是一天的截面，不是趋势。不用安全、忠诚或国籍的叙事框架。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 机构 | 第 2 步，每个公司名都先用计数核对 | 前沿创业公司：Mistral AI、Cohere、Perplexity |
| 岗位 | 第 2 步的职位关键词 | 数据工程或芯片设计职位 |
| 学历口径 | 第 3 到 5 步 | 印度的院校，用同样的方法建列表和核对 |

## 运行前先问清楚

1. 看哪些机构？有没有公司名会同时匹配到母公司或别的公司？
2. 哪些岗位？用职位名称里的哪些词？
3. 看哪个国家的院校？境外校区算不算？
4. 只看美国、看全球，还是都看？
5. 建列表和核对读档案最多能花多少 Credits？
