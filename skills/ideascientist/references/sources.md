# 主要来源与核查边界

核查日期：2026-10-13（America/Chicago）。本文档只记录第一手论文、作者公开仓库和作者数据卡。论文 v1 与当前产物分开记录；不以仓库 README 的自述替代完整复现。

## 1. 论文固定版本

- [arXiv abstract: 2610.04074v1](https://arxiv.org/abs/2610.04074v1)
- [完整 HTML](https://arxiv.org/html/2610.04074v1)
- [PDF](https://arxiv.org/pdf/2610.04074v1)
- 作者：Jiarui Liu 等；论文列出 Meta Reality Labs、FAIR at Meta 及合作高校。
- 公开日期：2026-10-02；页面许可 CC BY 4.0。

| 需要核查的内容 | 原文位置 |
|---|---|
| 问题定义、停止在 proposal | §1、§5.1 |
| 三 producer 与其他辅助角色 | §3、附录 A.1 / 表 2 |
| 每阶段输出 schema | 附录 A.2 / 表 3–7 |
| 奖励、引用门控 | §3.2、附录 B.1 / 表 8 |
| 14,500 / 200 / 277 | §4.2 |
| Base73.5 / Trained74.6 / DeepScientist60.6 | §5.2 / 表 1 |
| 50题×2人，非显著比较 | §5.2 / 图 2 |
| 组件与检索消融 | §5.3 / 图 3 |
| In-domain 是结构迁移二元量 | 附录 C |
| 目标输入泄漏抽查 0/50 | 附录 D |
| 训练资源、预算、selected checkpoint | 附录 E.1、F.4 |
| 参数记忆不能排除 | 附录 E.2 |

## 2. 作者代码

[上游仓库](https://github.com/jiarui-liu/IdeaScientist)。固定提交：`82a98a08772eab08d11fd097445afa4a8eaaa5b3`；本包保存固定提交源码 ZIP、原 README 和许可。版本与 SHA-256 见 [manifest.json](../assets/sources/manifest.json)。

- [README](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/README.md)：运行入口、数据、明确缺失的实验脚手架。
- [pyproject.toml](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/pyproject.toml)：Python、依赖、包许可。
- [LICENSE](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/LICENSE)：CC BY-NC 4.0；本 skill 不是作者或 Meta 官方发行。
- [roles.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/harness/roles.py)、[tools.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/harness/tools.py)：原始角色提示词、工具约束。
- [corpus.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/harness/corpus.py)：keyword-search、cutoff与数据库访问。
- [schema.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/vault/schema.py)：results-masked 原始 schema。
- [gap_finder.yaml](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/training/configs/gap_finder.yaml#L387)：核查到 cluster 8×8GPU、colocated generation。
- [run_grpo.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/training/run_grpo.py)：NeMo-RL依赖、运行驱动。
- [evaluate.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/scripts/evaluate.py)：分开计算 novelty aspects 的入口说明。
- [aggregate.py](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/ideascientist/evaluation/aggregate.py#L91)：`overall` 是 citation + quality + reference 平均，与表1定义不同。

直接读取原始角色/评价提示词应使用上述固定源码。Skill 的中文工作流和模板是适配产物；除明确标注原样摘录的许可文件外，不将本仓库文本称为“作者原始提示词”。

## 3. 作者数据

[Jerry999/SvalbardIdeaVault 固定数据卡](https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault/blob/64ab36be959afab06066f8c1e7ea292dba9362e5/README.md)，revision `64ab36be959afab06066f8c1e7ea292dba9362e5`。本包保存卡片快照，未打包 6GB 级完整数据。核查数据卡内容：

- 总记录 2,669,631；train14,149、validation195、test272、corpus2,655,015。
- 字段含 `problem_definition`、`intuition`、`proposal_masked`；没有独立 `challenge` 字段列。
- metadata 依 arXiv CC0 metadata terms；LLM生成注释为 CC BY4.0；底层论文版权仍属于原作者，数据集不再分发全文。
- 注释可能不准，不能当原论文作者表态；科学引用回到原论文。
- 核查时 viewer 出现日期字符串 `2026` 转 timestamp 失败；未验证全数据文件完整性或统计数量。

与论文计数不同的原因、原始277 test IDs与public272的关系尚未确认。完整复现须固定数据 revision、取得并比对 ID manifest；卡片数量是当前发布者自报，不是本包逐行复算结果。

## 4. 本包已经做和没有做的事

已核对方法、主表、指标定义、关键限制、公开入口与上述产物差异；整理成按需阅读的中文参考、模板和轻量工具；保存论文 PDF 与固定提交的完整代码 ZIP。没有运行原论文大规模训练、下载全文库、执行生成方案实验、重建全部论文表格或验证trained adapters达到原分数。

论文数字标“论文报告”；文件字段/配置标“代码核查”；网页数据卡标“发布者自报”；本包策略标“适配”。后续发现版本变化时更新锁与差异记录，不静默改动复现依据。
