# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 95 到 135 Credits：计数约 15，其余是抽检读取。超过 140 之前它会先停下来问你。

```text
用 Metix AI Platform 回答一个问题：招聘岗位点名了哪些 AI 编程工具，各有多少？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），只用 querySpecByEntity.job 里的字段。size 1 的计数花 1 Credit；没有结果的搜索不收费。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 140 Credits 之前先停下来问我。

2. 工具。Claude Code、Cursor、GitHub Copilot、Codex、Windsurf，在职位描述里匹配（字段 "description"，操作符 match）。

3. 当心普通词。match 要求每个词都出现，但不要求连在一起。Claude Code 和 GitHub Copilot 按名称匹配没有问题。Cursor、Codex、Windsurf 同时也是普通词（数据库游标、食品法典、帆板运动）。

4. 先抽检再相信。每个工具读 40 到 60 条描述，检查名称附近是不是 AI 编程的上下文。无关的超过 5%，就改成只在同一段描述里还提到另一个 AI 编程工具时才计入，再对收紧后的条件抽检一次。只看单词的计数也保留，让读者看到定义对数字的影响有多大。

5. 计数。每个工具算全球和 location.country eq "United States" 两次，被收紧的工具再算一次只看单词的数量，最后算一次"至少提到五个之一"。大约 15 Credits。

6. 清洗。不合并重复发布，直接说明。

7. 分组。一个文件写清每个工具的定义，被收紧的标为下限。

8. 输出。写出 data/tools.json，带 "unit": "jobs" 和快照日期，每个工具写计数、美国计数，有的话写只看单词的计数，再写"至少提到一个"的计数。运行前后各调用一次 GET /auth/key/status，余额差就是花费。

9. 图表。每个工具一根条形，排序，领先的高亮，被收紧的工具用斜线条，背后画一个只看单词时的轮廓。标题写结论。

10. 局限。提到一个工具不等于要求会用它，有的描述只是介绍团队在用什么。被收紧的工具是下限。这是某一天的截面，不是趋势。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 工具 | 第 2 步，新工具在第 4 步抽检 | 加上 Gemini Code Assist 或 JetBrains AI |
| 市场 | 第 5 步 | 按国家计数，或者只看一个行业 |
| 字段 | 第 2 步 | 改成搜标题，找围绕某个工具设的岗位 |

## 运行前先问清楚

1. 看哪些工具？它们的名字会不会有别的意思？
2. 看职位描述还是标题？
3. 看全球，还是某一个国家？
4. 抽检读描述最多能花多少 Credits？
