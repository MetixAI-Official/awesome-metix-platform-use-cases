# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 245 到 320 Credits：计数约 95，其余是抽检读取。超过 320 之前它会先停下来问你。发布的每个数字都是计数，读取只用于抽检。

```text
用 Metix AI Platform 回答一个问题：雇主在招聘岗位里点名的 AI 编程助手和 Agent 框架，需求和把它们列为技能的人相比如何？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费）。岗位用 querySpecByEntity.job，匹配 "description"；档案用 querySpecByEntity.profile，匹配 "skills"。size 1 的计数花 1 Credit，所以每个数字都按计数来设计。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 320 Credits 之前先停下来问我。

2. 工具。编程助手：Claude Code、Cursor、GitHub Copilot、Codex、Windsurf。Agent 框架和协议：LangChain、LangGraph、LlamaIndex、CrewAI、AutoGen、DSPy，以及 Model Context Protocol（匹配 "model context protocol"）。

3. 每个名称都先抽检再相信。match 要求每个词都出现，但不要求连在一起。每个工具读 40 到 60 条职位描述，检查名称附近是不是 AI 的上下文。Cursor、Codex、Windsurf 同时也是普通词；无关的超过 5%，就改成同一段文字里还提到另一个 AI 编程工具时才计入，岗位和档案都这样改，然后再抽检一次。

4. 有歧义的工具不进比值。收紧之后也数一下它们的档案。如果只剩几百个档案，比值主要反映的是定义本身，所以只在需求图里作为下限出现，不参与任何供需比较。

5. 计数。每个工具算四次：岗位和档案，各分全球和 location.country eq "United States"。所有人数都要过小格子规则（少于 10 写成 "<10"）。

6. 维度，全部用计数。同一个岗位同时点名两个编程助手的次数。至少点名一个助手的岗位，按国家（最大的 10 个加其他）和一份挑选出的行业列表计数（说明这不是排名，一个岗位可以属于多个行业）。美国的薪资下限：点名任意助手的岗位，以及作为对照的标题含 "software engineer" 的岗位，条件是 salary.currency eq "USD"，再分别数 salary.annual_min 不低于 100000、150000、200000、250000 的数量。

7. 当心定义本身决定了答案。一个定义为"和另一个工具一起被提到"的工具，一定会和别的工具同时出现，所以同时点名的比例只画按名称匹配的工具。

8. 输出。写出 demand.json、co-mentions.json、countries.json、industries.json、pay.json（"unit": "jobs"）和 supply.json（"unit": "profiles"），每个文件都带快照日期和来源查询文件。运行前后各调用一次 GET /auth/key/status，余额差就是花费。

9. 图表。双向图：档案向左、岗位向右，同一刻度；每个档案对应的岗位数，对数刻度，画一条一比一的线；同一个比值拆成美国和美国以外；各编程助手的岗位数，下限用斜线；同时点名的比例；按国家、按总数缩放；行业分两组；薪资画两组达到各档的比例。每张图的标题都写结论。

10. 局限，在第一张图之前说清楚。岗位每天刷新，档案的技能是本人填写、更新慢，越新的工具越跟不上，所以比值是需求和已公开技能之间的差距，不是和实际技能的差距。提到一个工具不等于要求会用它。不合并重复发布。这是某一天的截面，不是趋势。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 工具 | 第 2 步，每个都在第 3 步抽检 | 向量数据库：Pinecone、Weaviate、Qdrant、pgvector |
| 对比维度 | 第 6 步 | 把国家拆分换成资历或职能 |
| 市场 | 第 5 步 | 只看一个国家：每次计数都加上它的 location.country |

## 运行前先问清楚

1. 看哪些工具？有没有名字会有别的意思？
2. 只看需求，还是需求和供给对比？供给要用档案技能，并且要过小格子规则。
3. 哪些拆分维度重要：国家、行业、薪资？
4. 抽检读描述最多能花多少 Credits？
