# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍花 6 Credits，全部是计数。超过 10 之前它会先停下来问你。

```text
用 Metix AI Platform 回答一个问题：美国推理岗位写出来的薪资下限是多少？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），读薪资规则：对 salary.annual_min 做比较时，同一个 all 节点里必须用 eq 固定 salary.currency；金额是在同一币种内换算成年薪，不做跨币种换算。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 10 Credits 之前先停下来问我。

2. 人群。美国在招岗位，标题匹配 "inference"、"model serving"、"llm serving" 中任意一个，排除匹配 "causal" 或 "statistical" 的标题，并且 salary.currency eq "USD"、salary.annual_min 存在。

3. 分母也要算。去掉薪资条件，用同样的标题条件算一次美国总数，让读者知道有多大比例的岗位写了薪资。

4. 不读记录也能分档。分别数 salary.annual_min 不低于 150000、200000、250000、300000 的岗位，相邻两个数相减就是每一档。六次计数，6 Credits。

5. 核对。各档相加必须等于写明薪资的总数；对不上就停下来说明。

6. 清洗。不合并重复发布，直接说明。

7. 分组。15 万以下、15 万到 20 万、20 万到 25 万、25 万到 30 万、30 万及以上。

8. 输出。写出 data/bands.json，带 "unit": "jobs"、快照日期、写明薪资的数量、美国总数和每一档。运行前后各调用一次 GET /auth/key/status，余额差就是花费。

9. 图表。按档位顺序画竖条，最大的一档高亮，大数字旁边写出写明薪资的岗位占比。标题写结论。

10. 局限。写出来的是底薪区间的下限，不含奖金和股票。愿意公开薪资的公司可能和不公开的不一样。样本很小。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 岗位 | 第 2 步 | 用其他卡片里的标题条件 |
| 币种和国家 | 第 2、3 步 | 英国用 GBP，德国用 EUR |
| 衡量方式 | 第 4 步 | 用 salary.annual_max 看区间上限 |

## 运行前先问清楚

1. 看哪些岗位，哪个国家、哪种币种？
2. 看区间下限、上限，还是两者都看？
3. 档位的边界怎么定？
