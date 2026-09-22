# 启动提示词

把下面这段提示词交给一个能访问 Metix AI Platform 的 agent：装好 [metix-skills](https://github.com/MetixAI-Official/metix-skills)、接上 MCP 服务，或者直接用 REST 并设置好 `METIX_KEY` 都可以。完整跑一遍大约花 500 到 600 Credits：两部分发布用的计数 353，查找并读取核对切片和职位约 110，检验定义和确定切片大小的计数 40 到 140。超过 650 之前它会先停下来问你。发布的每个数字都是计数，读取只用于核对定义。

```text
用 Metix AI Platform 回答两个问题：在公开资料中写明自己属于 Meta Superintelligence Labs 的人里，有多少人在 2025 年 6 月实验室成立时已经在 Meta 工作？其余的人是从哪里来的？另外，Meta 可见的 AI 人员分布在哪些部门，这个实验室在其中处于什么位置？只通过公开的 Platform 访问（REST 地址 https://mira-api.metix.ai、MCP 服务或 metix-skills），密钥从 METIX_KEY 读取，任何时候都不要打印密钥。

1. 先读规则再查询。调用 GET /contract（免费），所有条件只用 querySpecByEntity.profile 和 querySpecByEntity.job 里的字段；再读 GET /docs/api/people（免费）。描述同一份工作的条件要放在同一个 has_experience 里，才能保证说的是同一份工作。文本字段按词匹配，顺序不限，不分大小写；current_function、current_seniority、experience.seniority 和 experience.company.type 只取固定值，用 eq 或 in。一次查询最多 64 个条件，嵌套最多 6 层。size 1 的计数花 1 Credit，查不到任何人时不收费；搜索每返回 25 个 ID 花 1 Credit，读取详情每 5 条记录花 1 Credit，所以每个要发布的数字都按计数来设计。每个查询先加一个什么也匹配不到的词发一次：Platform 会按限制检查查询，结果为空不收费。开始和结束时各调用一次 GET /auth/key/status（免费）查余额，总花费超过 650 Credits 之前先停下来问我。

2. 范围。当前在 Meta 工作（experience.company.name match "Meta" 且 experience.is_current eq true，放在同一个 has_experience 里），并且 headline 或 current_title 匹配 superintelligence 或 MSL。用计数确认 company.name eq "Meta" 得到同样的总数，说明这个名字没有匹配到别的公司；再确认 Facebook 在 Platform 上就是同一个雇主，不能当作单独的检验。以前在 Meta 的工作，指雇主名为 Meta、Facebook、Instagram、WhatsApp 或 Oculus 的经历。实习指 experience.seniority eq "Intern" 或 experience.title 匹配 intern 的经历，在同一条经历里判断。另外统计较窄的定义（只写 superintelligence），并作为背景统计写了 FAIR 却没写实验室名称的 Meta 在职资料。

3. 先核对再计数。搜索结果按匹配程度排序，只看最前面会让这个群体显得比实际更干净。所以要读完整的切片：size 25 的搜索花 1 Credit，同时返回总数，25 人以内的切片会完整返回。分五个切片读约 60 份资料（某个州里 2025 年 6 月前没有 Meta 经历的人，两个城市里有这类经历的人，Meta 经历没有开始日期的人，某个州里写 MSL 但没写 superintelligence 的人），用 POST /entity/v1/profiles/detail-by-id，_source 只取 headline、current_title、current_function 和经历里的 company.name、title、start_date、end_date、is_current、seniority，不取姓名。报告其中有多少人写的是在这个实验室工作，确认老员工以前在 Meta 有正式工作而不只是实习，并找出名单漏掉的 Meta 公司名称。子团队的每个词、Microsoft 群体的一个完整切片和所有在招职位，都用同样的方法读。读到的记录不能出现在任何公开文件里。

4. 分组。分界日期是 2025-06-01。统计总数；以前在 Meta 有经历、且开始于分界日期之前的人；去掉实习后的同一个数；以及留任的人：有一条非实习的 Meta 经历开始于分界日期之前，并且仍在进行或 experience.end_date gte "2025-05-01"（这两个条件用 any 放在同一条经历里）。回流的人等于非实习的数减去留任的数，前实习生等于第一个数减去非实习的数，新加入 Meta 的人等于总数减去第一个数；后三组合起来是外部招聘。较窄的定义也统计总数、以前的经历和留任三个数；写 superintelligence 的 Microsoft 在职资料统计四组，分界日期 2025-11-01，结束日期 2025-10-01。

5. 日期。统计以前的 Meta 经历开始于以下每个日期之前的人数：2012-01-01、2014-01-01、2016-01-01、2018-01-01、2020-01-01、2022-01-01、2023-01-01、2024-01-01、2025-01-01、分界日期、2025-07-01、2025-08-01、2025-09-01、2025-10-01、2026-01-01 和 2026-04-01；相邻两个日期的差就是一段首次加入的时间。去掉实习再做一遍，做到分界日期为止。对留任的人，统计当前 Meta 经历开始于以下每个日期当天或之后的人数：2025-01-01、2025-04-01、2025-06-01、2025-07-01、2025-08-01、2025-09-01、2025-10-01、2026-01-01 和 2026-04-01，这样每个人按最新的职位归入一段。Microsoft 统计 2012、2016、2020、2023、2025-01-01 和它的分界日期之前的人数。个人资料的更新有滞后，所以要按开始月份统计所有资料里的 Meta 经历，说明最后一个完整的月份是哪个月。

6. 来源。对外部招聘的人（范围内、不属于留任的人），统计一条 experience.end_date gte "2025-01-01" 的非实习经历，雇主依次为：OpenAI、DeepMind、Anthropic、xAI、Thinking Machines、Apple、Scale AI、Google、Microsoft、Amazon 或 AWS、NVIDIA；最后是 experience.company.type eq "Educational"，这一行实习也算。每一行都排除前面各行已经匹配到的人，剩下的算作其他雇主或没有。对整个群体，统计以前在 Google 或 DeepMind、OpenAI、Anthropic、Apple、Microsoft、Amazon 或 AWS 有过非实习工作的人；这些行会重叠。

7. 岗位、团队、地点和职位。对整个群体和外部招聘的人，分别统计 current_function eq Research、Engineering and Technical、Product，以及 current_function exists。对当前职能是 Research 的人，在实验室里和作为基准的其他 Meta 研究人员里（当前在 Meta、职能是 Research、没写实验室名称），分别统计 current_seniority 为 Senior、为 Manager 或更高级别、有级别，以及有 Doctorate 学历的人；整个群体和外部招聘的人也统计博士。统计 headline 或 title 里提到 FAIR、TBD、infra 或 infrastructure、PAR 或 product applied research 的人。统计 location.country 为 United States，location.state 为 California、New York、Washington，加州境内的湾区城市，以及 United Kingdom。对 Meta 在招职位（is_open eq true、company.name match "Meta"，并且标题匹配 superintelligence 或 MSL，或者描述匹配 superintelligence labs），统计总数、标题带 research 的职位、Menlo Park、San Francisco、New York、写明 min_experience_months 的职位和其中不超过 36 个月的职位、资历标签、2026-09-01 以来发布的职位，以及 Meta 全部在招职位。

8. 输出。写出汇总文件，每个都带 "unit"（"profiles" 或 "jobs"）、快照日期和来源查询文件。每个 1 到 9 人的计数都写成 "<10"。一段日期如果只有 1 到 9 人，就和相邻的一段合并，但不能跨过分界日期。某个公开的合计里，隐藏的格子加起来如果是 1 到 9 人，就再隐藏一个格子。较窄的定义和 Microsoft 群体只分到公开的计数之间每个差值都是 0 或至少 10 的程度。分母不少于 30 才发布比例。写任何文件之前，检查读者能算出的每个差值；写出的任何文字里都不写个人姓名，包括新闻里点名的人；链接新闻报道可以。

9. 图表。首次加入的各段画成时间线，标出分界日期，后面是新加入 Meta 的人按月的分布，Microsoft 画在同一条时间轴上；四组画成一根条形，较窄的定义和 Microsoft 放在下面；外部招聘的人按刚离开的雇主分组，五家 AI 实验室放在一起；留任的人和外部招聘的人的当前职能；实验室研究人员与基准的博士比例和级别；子团队的提及；各州；在招职位的地点。数值直接标在条上，每张图的标题用中性、客观的措辞写出结论。

10. 局限。这个范围是主动写明实验室的人，不等于实验室本身：只写 FAIR 或什么都没写的人不在其中，新加入的人和老员工写明的比例也可能不同。计数是可见的资料，不是员工人数；过时的资料也算作在职，所以也不保证是下限。有些资料已经过时，最近几个月的数字偏少。只写年份的日期按 1 月算，会把一些人移到分界的另一边，要说明是哪个方向。新增一条 Meta 经历只是调岗人数的下限，很多团队调动不会新增经历。来源依据的是经历的结束日期。Microsoft 群体规模小，还包括招聘人员。在招职位只是某一天的情况。用中性的动词（加入、离开、调动、招聘），除第 17 步职位里写明的基本薪资范围外，不涉及薪酬。

11. 版图的范围。Meta 可见的 AI 人员（P2）指有第一部分那条 Meta 在职经历、并且 headline 或 current_title 写有 AI 词的人：machine learning、ML、deep learning、computer vision、NLP、natural language processing、LLM、LLMs、large language models、reinforcement learning、generative AI、GenAI、artificial intelligence、superintelligence、MSL 或 FAIR；单独的 AI 只在 current_title 里算。实验室以外的人还要满足三个条件：在同一个 has_experience 里有一条 experience.company.size eq "10,001+" 的 Meta 在职经历；current_function 不是 Human Resources、Sales、Marketing、Administrative、Finance & Accounting、Legal、Customer Service 或 Real Estate；当前职位里没有 marketing、sales、recruiter、recruiting、sourcer、sourcing、talent、administrative、assistant、counsel、attorney、paralegal、accountant、communications 或 partnerships。把这三个条件各自和两个实验室名称条件放进同一个 any，这样第一部分的实验室成员全部留在 P2 里，两部分说的是同一群人。文本字段的词表用 in 发送：效果和每个词一个 match 条件相同，还能让每个查询保持在 64 个条件以内。

12. 核对版图。按 P2 的完整切片读至少 100 份资料（一个州或国家加一小段 total_experience_months，匹配到的全部读完），只取 headline、current_title、current_function、summary，以及当前经历的职位、描述、公司名称和规模，不取姓名，报告其中做 AI 工作的比例，必须达到 90%。确定词表之前，先检验读取中发现的陷阱：headline 里单独的 AI 多半是流行词；research scientist 和 research engineer 按词匹配，会把人员研究、调查科学、光子学，以及 Reality Labs Research 的软件工程师都算进来；在美国以外，Meta 这个名字还会匹配到别的公司。部门词（GenAI、generative AI、AR 和 VR 相关词、infra）也各读一个完整切片，据此判断每个词指的是团队还是话题，以及部门的先后顺序。

13. 部门和规模。统计美国的 Meta 在职资料数，以及规模为 10,001+ 的 Meta 在职经历在美国和美国以外各有多少，这样没有一个计数会变成 100000+。把 P2 的每个人归到 headline 或 current_title 里第一个出现的部门，顺序如下：实验室（superintelligence、MSL）；FAIR；Reality Labs，加上 AR、VR、XR、augmented reality、virtual reality、mixed reality、wearables、smart glasses 和 Oculus；infra 或 infrastructure；ads、monetization 或 advertising；ranking、recommendation、recommendations、recommender 或 recsys；integrity；Instagram、WhatsApp、Messenger 或 Threads；GenAI；以及都没写的人。对每个部门和整个 P2，统计总数、Research 和 Engineering and Technical 两种职能、经理及以上、博士、在美国、有 Bachelor 学历，以及 Bachelor 学历来自 cases/china-educated-ai-talent-2026/queries/institutions.json 里中国大陆院校的人。实验室的总数、职能、博士和美国人数就是第一部分对同一群人的计数。

14. 职能、级别和职位。对实验室和 P2，统计职位带数据类词（data、annotation、annotator、labeling、prompt、knowledge expert、rater、evaluator）且职能不是 Research 的人，再统计职位不带这些词的 Engineering and Technical、Product（连同 Design 和 Project Management）以及没写职能的人；research 用第 13 步的 Research 计数，other 是剩下的人。统计 current_seniority 为 Intern、Specialist、Senior、Manager、Head 或 Director 的人；Vice President 及以上等于经理及以上减去 Manager、Head 和 Director。统计当前职位包含 machine learning engineer、software engineer、research scientist、research engineer、engineering manager、product manager、program manager、data scientist、data engineer、prompt engineer、production engineer 和 director 的人，保留人数最多的十个。

15. 技术方向。对基础模型和 LLM、后训练和对齐、多模态和感知、AI 基础设施、智能体、排序和推荐、AR、VR 和设备、安全和评估这八个方向，按 headline 或 current_title 里的短语或 skills 里的单个词统计实验室和 P2，按标题里的短语或描述里的单个词统计 Meta 的 AI 职位（第 17 步）。Meta 每条职位描述都有一段讲增强现实和虚拟现实的固定文字，大多数还提到 responsible AI，而短语在长文本里会拆成词分别匹配，所以选描述用词之前先读一个完整的职位切片；词表见 queries/mapping.json。

16. 来源和流动。对实验室和 P2，统计以前在 Google 或 DeepMind、OpenAI、Anthropic、Apple、Microsoft、Amazon 或 AWS、NVIDIA、ByteDance 或 TikTok 有过非实习工作的人，以及在 Stanford、Carnegie Mellon、Berkeley、Massachusetts Institute of Technology、Urbana 和 Indian Institute of Technology 有任何学历的人。中国大陆本科的比例只有在每个格子都不少于 20 人时，才按级别拆分（Intern、Specialist 和 Senior 对比经理及以上）。统计 2025-06-01 以来的流动，两个方向用同样的时间窗，Meta 和 P2 是同一个雇主（名称为 Meta 且雇主规模为 10,001+；Facebook、Instagram、WhatsApp 和 Oculus 按名称）：流向 X 指一条 2025-06-01 或之后开始的 X 非实习在职经历、一条 2025-05-01 或之后结束的 Meta 非实习经历，并且目前没有任何名称为 Meta 的在职经历（不论规模）；从 X 流入指一条 2025-06-01 或之后开始的 Meta 非实习在职经历、一条 2025-05-01 或之后结束的 X 非实习经历，并且目前不在 X 任职。统计 OpenAI、DeepMind、Anthropic、xAI、Thinking Machines、Microsoft、Apple、Amazon 或 AWS、NVIDIA、同一条经历里不含 DeepMind 的 Google，以及 Meta 名称以外的任何雇主；某一行不少于 10 人时，再加上 AI 词统计一次。

17. 职位和薪资。取 posted_date gte "now-180d"、标题含 P2 的 AI 词或 AI、且不含那些非技术职位词的 Meta 职位，按职位族依次归类，取第一个匹配：research scientist；research engineer；software engineer、machine learning engineer、ML engineer 或 AI engineer；数据类职位；product manager、product management、program manager 或 designer；其他。对美国、以美元计、同时写明 salary.annual_min 和 salary.annual_max 的职位，统计全部以及前三个职位族各有多少；达到 15 条的，再统计 annual_min 不低于 150,000、180,000、215,000 和 265,000，以及 annual_max 不低于 215,000、250,000、295,000 和 340,000 的职位数。这是职位里写明的基本薪资范围，不是实际薪酬。

18. 版图的输出。每个指标写一个汇总文件：data/map_size、map_units、map_functions、map_levels、map_titles、map_directions、map_sources、map_flows、map_postings 和 map_pay。每个 1 到 9 人的计数都写成 "<10"，分母不少于 30 才发布比例。列出读者能算出的每一个合计（各部门加起来是 P2，表里每一行加起来是它的总数，一个部门在美国的人包含在它的总数里，第二部分的实验室格子包含在第一部分对应的格子里，一行流动里带 AI 词的部分包含在这一行里），逐个隐藏最小的格子，直到算不出任何 1 到 9 人的群体。第一部分已经发布了实验室的职能，所以当拆出数据类职位会留下这样的差值时，把实验室的 other 和 none 合并。任何一项检查不通过就什么也不写。

19. 版图的图表和局限。组织版图画成一棵树：P2、各部门，实验室和第一部分的几个小组挂在实验室下面；然后是各部门的职能和级别、技术方向（资料对比职位）、来源、流动（成对的条形），以及各职位族写明的薪资区间。要说明：部门是人们自己写的，不是 Meta 的组织架构；P2 数的是资料，不是员工，准确率由核对测得；职位只是某一天在招的岗位，同一个岗位在几个城市发布会按城市各算一次；流动依据的资料滞后，日期只到 2026 年 4 月，而且跨过了 2025 年 10 月 Meta AI 部门的裁员；只看一家公司无法衡量招聘难度，这一项不在范围内。
```

## 怎么改成你自己的问题

| 想改的 | 改哪里 | 例子 |
| --- | --- | --- |
| 实验室 | 第 2 步的雇主和实验室名称，并按第 3 步重新核对 | 写 Gemini 的 Google DeepMind 员工，或 Microsoft AI |
| 实验室成立的日期 | 第 4 步和第 5 步的分界日期 | Microsoft 超级智能团队用 2025-11-01 |
| 新人来自哪里 | 第 6 步的雇主顺序 | 加上 Mistral AI 或 Cohere |
| 版图的部门 | 第 13 步的顺序和词表，并按第 12 步重新核对 | 单列 WhatsApp，或者 Llama |
| Credit 上限 | 第 1 步、第 3 步和第 12 步 | 只跑第 1 到第 10 步，花费约 200 Credits |

## 运行前先问清楚

有人带着更笼统的问题来时，先把这几件事定下来，每一件都会改变查询或花费：

1. 哪些词表示一个人属于这个实验室？其中有没有词还有别的意思？
2. 哪些公司名称算同一个雇主，现在的和以前的都算吗？
3. 用哪个日期区分原本就在的人和后来加入的人？
4. 实习算不算以前在那里工作过？
5. 核对读取最多能花多少 Credits？
6. headline 里哪些词指的是团队，哪些只是话题？
