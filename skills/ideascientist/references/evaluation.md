# 实验、指标与可支持的结论

论文事实采用 [arXiv:2610.04074v1](https://arxiv.org/html/2610.04074v1)，公开实现观察日期为 2026-10-13。不要把论文报告、本地 smoke check 和自己生成的科研结果混为一件事。

## 1. 数据与公平比较

论文 §4 / §5 报告：arXiv 跨学科库约 4.7M 篇，其中约 2.8M 有全文；完成约 2.77M idea decomposition。训练目标来自 2026-01-01 起的 ML 方法论文，需可取得 LaTeX 且超过 70% 引文有可用全文；排除综述、立场、数据集/基准、纯经验工程报告。[§4](https://arxiv.org/html/2610.04074v1#S4)

| 论文划分 | 目标论文数 |
|---|---:|
| train | 14,500 |
| validation | 200 |
| test | 277 |
| 合计 | 14,977 |

三个角色共用同一划分。输入由目标论文抽出的 problem + challenge 构成，目标方法和测得结果不提供给运行中的 agent；参考产物用于训练或离线评价。最终论文表 1 是 277 个 test target 的 proposal 评价。[§4.2](https://arxiv.org/html/2610.04074v1#S4.SS2)

比较系统收到相同问题、输出 schema 与离线文献接口，禁用互联网，隐藏目标论文。AutoResearch 系统保留自己的 agent loop，但被要求完成 proposal 后停止，不继续实施实验。原生外部 loop 没有统一套用 IdeaScientist 每角色 turn caps；这限制了“完全等算力”解读。[§5.1](https://arxiv.org/html/2610.04074v1#S5.SS1)、[附录 E.1](https://arxiv.org/html/2610.04074v1#A5.SS1)

## 2. 三类 novelty 不能混称

| 指标 | 实际判断 | 尺度 |
|---|---|---|
| All | 相对完整比较库最近邻新增了什么，比较库可以含 cutoff 后工作 | judge 1–10 |
| Cutoff | 同样问题，但比较文献限定在 cutoff 以前 | judge 1–10 |
| In-domain | 是否存在有依据的跨 setting 结构迁移 | 二元 0/1 的比例 |

In-domain 得 1 必须同时交代源场景不同、具体借入机制、共享结构、目标适配。它并不是独立衡量“全部科学新颖性”的 1–10 分。来源：[附录 C](https://arxiv.org/html/2610.04074v1#A3)。

额外的 **Mechanism non-obviousness** 用两次 judge 调用：第一次只见问题与三篇 cutoff 前机制近邻，先独立提出候选；第二次才见待评 proposal，只能对冻结候选比较。四等级映射 0、1/3、2/3、1；候选无效则重试，不能把生成候选失败直接算作高新颖性。

Proposal quality 有 relevance、clarity、specificity、actionability、soundness、impact 六项，均为 1–10。Relevance 另见问题与 challenge，其余五项由 proposal 本身评分。它们是执行前代理指标，不包含独立实验验证。[附录 C](https://arxiv.org/html/2610.04074v1#A3)

## 3. 主结果应怎样读

下表只摘取论文表 1 同一 Qwen3.6-27B 骨干的关键行，数值为论文展示的 0–100 尺度。

| 系统 | novelty 平均 | quality 平均 | overall |
|---|---:|---:|---:|
| DeepScientist | 43.8 | 77.5 | 60.6 |
| IdeaScientist-Base | 66.9 | 80.0 | 73.5 |
| IdeaScientist-Trained | 68.8 | 80.4 | 74.6 |

来源：[表 1](https://arxiv.org/html/2610.04074v1#S5.SS2)。Table 1 的 `overall = (novelty_avg + quality_avg) / 2`，novelty_avg 平均三个 novelty 指标，quality_avg 平均六项质量。

按表中四舍五入数值计算：Trained 比 DeepScientist 高 **14.0 个评分点**；相对比例约 23.1%。Trained 比 Base 高 **1.1 个评分点**。不能用“RL 带来 14% 提升”替代这两种比较，也不能从 Base 的优势分解出未经控制的单个机制因果贡献。

人工盲评对 50 个随机 test target，每题两名评审；系统名隐藏。论文报告 Trained 对 DeepScientist、对自身 Base 的优势均未达统计显著。其余同骨干 baseline 的胜率达到论文报告的显著性。[§5.2 / 图 2](https://arxiv.org/html/2610.04074v1#S5.SS2)

消融包含 Report Writer alone → 加 Gap Finder → 加 Innovator，以及 Innovator 同域/跨域检索；这可支持流程组件在该基准上的贡献，不能证明迁移是所有任务唯一正确路径。[§5.3 / 图 3](https://arxiv.org/html/2610.04074v1#S5.SS3)

## 4. 时间切分的边界

检索 cutoff 是 2026-01-01。论文做了 50 个 model–paper title-only 查询：五个模型各查十篇 post-cutoff 论文，未发现可靠标题级回忆。作者明确承认这不能排除潜在、改写或方法层面的模型参数记忆。因此结论是**受控检索 cutoff 下的表现**，不是证明模型参数从未见过目标方法。[附录 E.2](https://arxiv.org/html/2610.04074v1#A5.SS2)

问题输入从全文逆向抽取也可能泄漏方法线索；作者抽查 50 例，报告 0/50。这个样本不能证明整个数据集零泄漏。[附录 D](https://arxiv.org/html/2610.04074v1#A4)

## 5. 当前公开产物与论文的差异

1. [固定 HF 数据卡](https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault/blob/64ab36be959afab06066f8c1e7ea292dba9362e5/README.md) 为 train 14,149 / validation 195 / test 272 / corpus 2,655,015；与论文 14,500 / 200 / 277 不同。未核对原始 ID manifest 前不能说是同一个 benchmark。
2. 公共 `evaluation/aggregate.py` 的 `overall` 平均 citation F1、六项 quality、十项 reference-match，且 novelty_average 只含 All / Cutoff；它**不是 Table 1 overall**。固定代码链接见 [sources.md](sources.md)。
3. `scripts/evaluate.py` 不单独完成 In-domain / non-obviousness，需要 `compute_novelty_aspects.py`。`--reference-report` 控制 reference reward 字段；省略它会影响公共 aggregator 的 overall。
4. 上游 README 明说未公开消融实验臂、人工研究脚手架和 LaTeX table builder。仓库存在相关指标代码不代表原始 runs、人工标注或全部表格能重建。

## 6. 使用 skill 评价自己的候选

把 proposal judge、引文核验、最近邻差异、迁移判据和实际 probe 结果分别报告。默认结果表记录：可解析/引用有效、主要最近邻、机制差异、迁移条件、六项质量及理由、最小可证伪实验、已完成验证。

要比较方法，先固定 task IDs、语料版本、模型版本、工具、预算、失败处理和 judge prompts。按固定目标总数作分母，失败目标记零并额外报告失败率。保留逐题输出；不能只挑成功样例或成功 run 平均。

本 skill 的结构校验脚本检查文件/字段与证据引用，不会自动证明文献穷尽、科学新颖性或方法有效。若要重算 Table 1，必须显式映射三个 novelty 与六项 quality，并标明使用 277 原 split 还是 272 public split；不要默用上游 `overall`。
