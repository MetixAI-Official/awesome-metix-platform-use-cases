# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 56 到 64 Credits：计数 8，其余是抽检读取。超过 70 之前它会先停下来问你。

```text
用 Metix AI Platform 回答一个问题：招聘标题里最常出现模型生命周期的哪个阶段，每个阶段在哪里招人？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），只用 querySpecByEntity.job 里的字段。搜索按 ceil(返回的 ID 数 / 25) 计费，所以 size 1 的计数花 1 Credit，没有结果的搜索不收费。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 70 Credits 之前先停下来问我。

2. 阶段。四组标题条件：预训练（pretraining、pre-training）、后训练（post-training、posttraining）、微调（fine-tuning、finetuning）、推理（inference、model serving、llm serving）。每个阶段用一个 any 节点。

3. 每个阶段用同一套防误判条件。match 要求每个词都出现，但不要求连在一起，所以 "pre-training" 也会命中 "Pre-licensed Training Provided"。要求标题里有一个机器学习相关的词（research、engineer、scientist、llm、model、ai、ml、technical），并排除 sales、customer、teacher、trainer、doctoral、pharmacy、licensing、licensed、causal、statistical。后训练不要加 "RLHF"，人力公司反复发布的数据标注岗位会把它淹没。

4. 先抽检再相信。最小的阶段（不到 100 个）把标题全部读一遍，其他阶段各读 50 个。报告有多少是无关的；超过 5% 就补充排除词，四个阶段一起改，并说明改了什么。

5. 计数。每个阶段算全球和 location.country eq "United States" 两次，size 1，一共 8 Credits。

6. 清洗。这里不合并重复发布，直接说明，不要猜一个修正值。

7. 分组。四个阶段就是四组，连同条件写在一个文件里。

8. 输出。写出 data/stages.json，带 "unit": "jobs" 和快照日期，每个阶段写全球数和美国数。运行前后各调用一次 GET /auth/key/status（免费），余额差就是花费。

9. 图表。每个阶段一根条形，按最大的那根缩放，推理高亮，每根标出数量和美国占比。大数字用推理和预训练的比值，不用某个计数。

10. 局限。只看标题：前沿实验室的很多人挂的是 "Member of Technical Staff" 这类通用头衔，所以每个数都是下限，比较的是招聘标题怎么写，不是团队规模。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 阶段 | 第 2 步 | 加上评测（"evals"、"model evaluation"），用同样的方法抽检 |
| 防误判条件 | 第 3 步 | 某个阶段噪音大时，收紧机器学习相关的词 |
| 地理范围 | 第 5 步 | 按几个国家分别计数，而不只是美国 |

## 运行前先问清楚

1. 看哪些阶段，每个阶段用标题里的哪些词？
2. 只看标题，还是也看职位描述？描述的噪音大得多。
3. 看全球，还是某一个国家？
4. 抽检读标题最多能花多少 Credits？
