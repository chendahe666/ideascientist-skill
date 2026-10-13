# 论文方法与输出契约

本页是中文释义与运行建议，不是作者提示词的逐字翻译。论文事实以 [arXiv v1，2026-10-02](https://arxiv.org/html/2610.04074v1) 为准；公开实现的固定版本见 [sources.md](sources.md)。

## 1. 先确定任务

论文的输入是一个明确的 **problem definition + challenge**，输出是有文献依据的研究方案。它没有自动选择所有研究方向，也没有用实施实验来证明生成方案有效。原始系统在 proposal 完成后停止。依据：[§1](https://arxiv.org/html/2610.04074v1#S1)、[§5.1](https://arxiv.org/html/2610.04074v1#S5.SS1)。

使用 skill 时先写出：具体输入、期望输出、现有方法、可观察的困难、允许的资源与比较条件。宽泛方向可以先整理成问题卡；未确认的困难标为假设。

核心思路是：目标领域某个困难，也许与另一个问题共享结构；找出源问题已经使用的机制，再解释如何适配到目标问题。一个领域名、一条引用或通用工具本身不构成迁移。依据：[§3.1](https://arxiv.org/html/2610.04074v1#S3.SS1)、[附录 C](https://arxiv.org/html/2610.04074v1#A3)。

## 2. 角色与交接

| 角色 | 输入和工作 | 输出 | 原始信息权限 |
|---|---|---|---|
| Orchestrator | 维护计划、安排角色、决定返工 | `plan.md` | 看中间文件；不检索或读论文 |
| Gap Finder | 沿指定挑战轴检查最近邻方法 | `gaps.md` | 检索书目信息、请求读者摘要 |
| Innovator | 针对已确认的 gap 寻找可迁移机制 | `candidates.md` | 同上 |
| Report Writer | 把通过筛选的机制展开成可实施方案 | `report.json` | 同上 |
| Reviewer | 检查同问题最近邻，质疑候选 | `scores.md` | 同上 |
| Paper Reader | 在隔离上下文读一篇全文，回答阅读目标 | `papers/<id>.md` | 唯一接收全文的角色 |

角色权限来自 [附录 A.1 / 表 2](https://arxiv.org/html/2610.04074v1#A1.SS1)。原系统按工具可用性隔离信息；普通聊天 skill 的角色分工本身不提供同等强制隔离。只有实际使用独立上下文与工具限制时，才能报告相应隔离已经落实。

固定代码的 producer / reviewer 文献接口是 `keyword_search`、`get_paper_biblio`、`read_paper`，文件操作通过 `edit_doc`；`get_full_text` 受角色 full-text cap 约束。角色只编辑自己的产物。原实验每个一阶角色最多请求20次阅读，Reader单次输入上限30,000 tokens。[tools.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/harness/tools.py)、[附录 A.1](https://arxiv.org/html/2610.04074v1#A1.SS1)

检索使用同一 keyword-search 接口，两个 regime 是查询写法，而不是两套工具：Gap Finder 先用同任务、同挑战术语做 4–8 个查询；Innovator 做 6–10 个机制查询，优先跨至少三个不同子领域。Review 回到同问题检索以检查最近邻。依据：[附录 A.1](https://arxiv.org/html/2610.04074v1#A1.SS1)。

## 3. 阶段输出必须回答的问题

### Gap Finder：最多两个 gap / 挑战轴

1. **Gap**：现有方法靠什么机制解决什么，哪一项机制假设留下了具体困难？
2. **Near misses**：最接近的工作与 ID；各自做到哪里、缺什么；通常至少两个真实最近邻。
3. **Methodological deficiency**：机制缺失、目标不匹配、表达限制等具体方法原因及证据。
4. **Why it matters**：谁受影响，补上后增加什么能力或认识。
5. **Evidence route**：怎样观测困难被解决；此阶段不提前写解决方案。

以上是 [表 3](https://arxiv.org/html/2610.04074v1#A1.SS2) 的释义。区别“作者承认的局限”“我们从实现推断的局限”“待实验确认的问题”。没有查到论文不等于没有先例。

### Innovator：每次一个候选

写清 intuition、攻击的 gap、源论文与借用机制、源问题为何有效、目标映射、共享结构、迁移假设、最近邻区别和最主要失败风险。改进旧候选时交代改了什么。

原始 intuition 阶段避免方程、伪代码、架构和超参数；先把机制关系说清楚，再由 Report Writer 实现化。来源类型分为新主题、远距离概念重组、加强已有弱连接。依据：[表 4](https://arxiv.org/html/2610.04074v1#A1.SS2)。

### Report Writer：一份 results-masked JSON

原论文表 5 要求以下内容；真正字段与嵌套类型以固定版本的 `vault/schema.py` 为准，不把本页名称当成 JSON Schema。

| 内容 | 要求 |
|---|---|
| title、topic relevance、one-sentence thesis | 题目、领域、30 个英文词以内且无指标数值的主张 |
| core problem、problem definition、key terms | 失败实例、正式输入输出、术语解释 |
| key novelty、related work | 中心机制、各子领域已有机制和未解决点 |
| method、model details | 数据流、模块、关键设计、训练目标与必要超参数 |
| comparison to SOTA | 对最近邻逐项说明实质差异 |
| proposed evaluation | 场景、基准、基线、指标、消融；全部写成计划 |
| falsifiable predictions | 每个预测配一个会推翻它的观察 |
| limitations | 3–5 项明确限制 |

出处：[表 5](https://arxiv.org/html/2610.04074v1#A1.SS2)。原输出用数据库 ID 内联引用，不包含测得的实验结果。实际项目已有结果时可以单独存证；不要把已有结果混进“尚未实施的预期”。

### Reviewer 与 Reader

Reviewer 输出 survive / revise / reject，给出引用证据和单个最强反对意见。revise 指定一个最弱维度。Reader 输出题目、短摘要、逐阅读目标回答，并定位到章节或公式。[表 6–7](https://arxiv.org/html/2610.04074v1#A1.SS2)

## 4. 原论文的训练机制

三个 producer 分别训练 LoRA，再组合进相同 harness；Orchestrator 固定。训练时下游角色接收**参考的上游产物**，而非另一角色现场生成的产物，便于把改进归到具体阶段。[§3.2](https://arxiv.org/html/2610.04074v1#S3.SS2)、[附录 B.1](https://arxiv.org/html/2610.04074v1#A2.SS1)

```text
r = 0.85 * g * (r_free + r_ref + r_cit) / 3 + 0.15 * r_proc
```

- `r_free`：不看目标答案的质量评价。
- `r_ref`：与从人类论文重建的对应阶段参考产物比对实质决策。
- `r_cit`：引用论文集合的 F1；文献集合重合不是科学正确性证明。
- `g`：格式、任务、已读引用、工具等门控；Gap / Innovator 另有方法性判据。
- `r_proc`：规则合规项；不因搜索或阅读次数多而额外加分。

`g=0` 清零 rubric 部分，保留 process 项。解析失败的 judge 响应重试后仍失败时排除，不伪造奖励。参考产物大部分由 Qwen3.6-27B 从人类论文重建，少量由 GPT-5.4 补齐；不是逐条人写的标准答案。[附录 B.1、D](https://arxiv.org/html/2610.04074v1#A2.SS1)

## 5. 本 skill 的适配边界

中文问题卡、URL 证据账本、最小 problem / transfer probe、预算和停止规则是本仓库的实用适配。正常调用 skill 不会自动获得论文 LoRA、2.77M 数据库、原论文训练效果或严格时间隔离。需要复现原系统时转到 [reproduction.md](reproduction.md)；评估结论转到 [evaluation.md](evaluation.md)。
