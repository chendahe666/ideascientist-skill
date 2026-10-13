# ideascientist skill

把 Meta 与高校合作的 [IdeaScientist 论文](https://arxiv.org/abs/2610.04074)整理为一个可安装、可追踪依据的科研 skill。Skill 名称：**`ideascientist`**。

这是独立整理的 skill，不是作者官方发布的模型。提供论文原件、固定版本代码、方法与实验说明，以及本地辅助脚本。日常使用由你的现有智能体执行“找缺口 → 找跨场景机制 → 写可检验方案”；完整上游训练和论文复现另有入口与限制说明。

## 安装与调用

下载本仓库，将 `skills/ideascientist` 文件夹复制到你的 Codex 用户技能目录：

- Windows：`%USERPROFILE%\.codex\skills\ideascientist`
- macOS / Linux：`~/.codex/skills/ideascientist`

如果目录已存在，先比较内容并备份；不要直接覆盖正在使用的版本。安装后重新打开会话，再调用：

```text
$ideascientist 请研究这个问题：……
现有方法的具体挑战：……
我的数据与计算预算：……
请给出有原始文献依据的缺口、可迁移机制，以及最小验证实验。
```

也可要求：“用 $ideascientist 解释论文的训练奖励和评估限制”，或“检查我是否具备运行上游代码的条件”。

## 包含什么

| 内容 | 位置 |
|---|---|
| Skill 入口及模式选择 | [SKILL.md](skills/ideascientist/SKILL.md) |
| 角色流程、引用记录和产物结构 | [workflow.md](skills/ideascientist/references/workflow.md) |
| 原论文方法 | [paper.md](skills/ideascientist/references/paper.md) |
| 实验数字、指标定义及证据边界 | [evaluation.md](skills/ideascientist/references/evaluation.md) |
| 上游运行/训练/评估，以及公开版差异 | [reproduction.md](skills/ideascientist/references/reproduction.md) |
| 原始来源及版本 | [sources.md](skills/ideascientist/references/sources.md) |
| 论文 PDF、未修改的上游代码 ZIP、数据卡 | [assets/sources](skills/ideascientist/assets/sources) |
| 初始化研究记录与结构校验 | [scripts](skills/ideascientist/scripts) |

未包含：多 GB 数据集、基础模型/训练适配器权重、API 密钥。我们没有运行论文训练，也没有验证论文实验成绩。论文正文与公开数据/配置/聚合实现的差异见复现说明。

## 不调用模型的本地操作

以下命令在 `skills/ideascientist` 目录运行，只依赖 Python 3.10+ 标准库：

先确认 `python --version` 指向可用解释器；如果 Windows 仅提供未安装的商店别名，请改用实际安装的 Python 路径。

```text
python scripts/prepare_upstream.py
python scripts/prepare_upstream.py --extract-to ./work/upstream
python scripts/init_run.py --run-dir ./runs/example --problem "具体任务的输入和目标输出" --challenge "现有方法的具体不足"
python scripts/validate_run.py ./runs/example
python scripts/test_helpers.py
```

新建记录的校验会报告尚未完成，这是预期行为。需要真实阅读文献并填写各阶段产物后再校验；结构通过也不代表事实、创新性或实验效果已被证明。

## 版本与许可

- 论文：`2610.04074v1`，2026-10-02，作者许可 CC BY 4.0。
- 上游代码：[`jiarui-liu/IdeaScientist`](https://github.com/jiarui-liu/IdeaScientist)，固定 commit [`82a98a08772eab08d11fd097445afa4a8eaaa5b3`](https://github.com/jiarui-liu/IdeaScientist/tree/82a98a08772eab08d11fd097445afa4a8eaaa5b3)，CC BY-NC 4.0。
- 数据卡：`Jerry999/SvalbardIdeaVault`，固定 revision `64ab36be959afab06066f8c1e7ea292dba9362e5`。
- 本 skill 的整理文档与新增脚本：CC BY-NC 4.0。原件各自保留原许可。[署名与修改说明](NOTICE.md)

源文件哈希可通过 `prepare_upstream.py` 验证。验证记录只证明包结构、脚本行为和原件完整性，不证明科研能力或上游结果复现。
