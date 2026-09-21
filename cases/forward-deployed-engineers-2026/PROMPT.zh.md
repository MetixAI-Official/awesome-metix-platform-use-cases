# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 130 到 145 Credits：计数 13，其余是用来挑国家的读取。超过 150 之前它会先停下来问你。

```text
用 Metix AI Platform 回答一个问题：哪些国家在招前线部署工程师（forward-deployed engineer）？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），只用 querySpecByEntity.job 里的字段。size 1 的计数花 1 Credit。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 150 Credits 之前先停下来问我。

2. 人群。标题匹配 "forward deployed" 的在招岗位。这个词组很少有别的意思；读 25 个标题确认一下。

3. 先算总数。一次全球计数，size 1。

4. 挑国家。读大约 500 个岗位的国家，看出现了哪些国家。搜索结果有它自己的排序，不是随机样本，所以这一遍只用来挑国家，绝不要用它算出的比例发布数字。

5. 分国家计数。对这一遍里最大的 12 个国家，用 location.country eq 国家名各算一次，size 1。其他国家和地区等于全球数减去它们的和。

6. 清洗。重复发布和挂在多个城市的岗位没有合并；说明这些数字衡量的是这个头衔的招聘声量，不是职位数。

7. 分组。12 个国家加其他国家和地区，列表写在脚本里。

8. 输出。写出 data/countries.json，带 "unit": "jobs"、快照日期、全球数，以及每个国家的计数和占比。运行前后各调用一次 GET /auth/key/status，余额差就是花费。

9. 图表。每个国家一根条形，按全球总数缩放，美国高亮，其他国家和地区用斜线条放在最后。标题写结论。

10. 局限。只看标题；做同样工作但头衔不同的岗位（比如 solutions engineer）没有被算进来。这是某一天的截面，不是趋势。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 岗位 | 第 2 步 | "solutions engineer"、"applied AI engineer"、"AI deployment" |
| 拆分方式 | 第 4、5 步 | 一个国家里的城市，或者一份公司名单 |
| 时间窗口 | 第 2 步 | 加上 posted_date gte now-30d，只看最近发布的岗位 |

## 运行前先问清楚

1. 看哪个头衔，它会不会有别的意思？
2. 按国家、城市还是公司拆？
3. 看所有在招岗位，还是只看最近发布的？
4. 挑国家的那一遍读取最多能花多少 Credits？
