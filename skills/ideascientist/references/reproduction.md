# 上游代码运行与复现路线

先阅读 [sources.md](sources.md) 的版本、许可与差异记录。以下命令基于实际公开 README/入口的说明；本 skill 发布时没有下载全库、调用付费模型或启动 GPU 训练。

**关键复现差异：**固定版上游 `evaluation/aggregate.py` 的 `overall` 不是论文 Table 1 的 `overall`。必须另行组合 All、Cutoff、In-domain 与六项质量，不能直接把公共 aggregator 的数值作为论文表1复现。另有 public272 / paper277 test 数量和64GPU / 320H100拓扑差异，下文分别说明。

## 1. 分清三种使用模式

| 模式 | 可以得到什么 | 不能据此宣称什么 |
|---|---|---|
| skill adaptation | 用现有 Codex 工具执行 Gap → Transfer → Review → Proposal | 原论文 trained checkpoint 的表现 |
| upstream harness | 运行作者代码，保留原始工具日志与产物 | 没有数据与端点也能直接运行 |
| paper reproduction | 原 split、语料、骨干/LoRA、预算、judge 与结果聚合对齐 | 只 pip install 就完整复现 |

上游代码和数据分开发布，固定版本与哈希见 [manifest.json](../assets/sources/manifest.json)。本包已包含 `assets/sources/upstream-code.zip`；提取到独立目录后再运行。源码提交为 `82a98a08772eab08d11fd097445afa4a8eaaa5b3`，数据卡 revision 为 `64ab36be959afab06066f8c1e7ea292dba9362e5`，不要把不断变化的 `main` 当成复现版本。

## 2. 运行前需要的资源

- Python >=3.10；上游 core 依赖 numpy、requests、PyYAML，额外依赖组为 vault / embed / analysis。
- 支持 tool calling 的 OpenAI-compatible 模型端点与真实模型 ID；训练角色适配器另行准备。
- SQLite vault、全文表、results-masked records、引文表，以及已构建的 keyword index。
- novelty 检索所需 embedding vectors 与 query encoder；重建 embedding 通常需 GPU。
- 精确复现训练另需 NeMo-RL 环境、多 GPU 资源、三个角色的数据与参考产物。

依据：固定版 `pyproject.toml`、`README.md`、`harness/corpus.py` 与 `training/run_grpo.py`（链接见 [sources.md](sources.md)）。上游 core 安装并不安装完整训练环境；目前没有锁定一个经过此 skill 验证的 NeMo-RL commit。

## 3. 准备 upstream harness

在独立环境与上游 checkout 中执行，避免把训练依赖混入 skill 本身。

```bash
python -m venv .venv
# 激活虚拟环境后：
python -m pip install -e .
python -m pip install -e '.[vault,embed,analysis]'
```

以下为 PowerShell 配置示例；API key 由本地秘密配置提供，不写进 skill、日志或仓库。

```powershell
$env:IDEASCIENTIST_BASE_URL = 'http://localhost:8000/v1'
$env:IDEASCIENTIST_MODEL = 'Qwen3.6-27B'
$env:EMBEDDING_BASE_URL = 'http://localhost:8100/v1'
$env:EMBEDDING_MODEL = 'Qwen3-Embedding-0.6B'
$env:QWEN3_EMB_MODEL_PATH = 'Qwen/Qwen3-Embedding-0.6B'
$env:IDEA_VAULT_DB = 'data/idea_vault.db'
$env:IDEASCIENTIST_KEYWORD_INDEX = 'data/keyword_index.db'
$env:IDEASCIENTIST_CUTOFF_DATE = '2026-01-01'
```

端点若需要密钥，再设置 `IDEASCIENTIST_API_KEY`。`CONTEXT_WINDOW` 必须匹配真实服务窗口；README 的 32768 只是较小窗口示例，不能让 49K 训练序列自动变得可用。

上游推荐模型工具解析配置：

```bash
vllm serve <model> --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser hermes
python -m ideascientist.serving.query_server --port 8100
```

这是两个不同服务进程。模型返回工具 prose 而 `tool_calls` 为空时可用 `IDEASCIENTIST_TEXT_TOOLS=1`；先记录解析错误再切换，不把静默停滞当成研究失败。Query server 注入检索 instruction，不能随意用未匹配的 pooling endpoint 替代后继续声称检索等价。

## 4. 数据不是 HF 下载后自动成为 SQLite

公开 HF 字段为 `arxiv_id`、metadata、`problem_definition`、`intuition`、`proposal_masked` 等；数据卡未列出独立 `challenge`、完整 SQLite schema、全文、引文表或角色参考产物。因此不能把其 JSONL 路径填入 `IDEA_VAULT_DB` 就认为满足 harness 输入。

如需自行建库，上游入口为：

```bash
python scripts/build_vault.py init
python scripts/build_vault.py crawl --start 1986-01-01 --end 2026-06-18
python scripts/build_vault.py fulltext
python scripts/build_vault.py citations
python scripts/build_vault.py decompose
python scripts/build_vault.py index
python scripts/build_vault.py splits
```

先检查各阶段 `--help`、`--limit` 和已有文件，再决定运行范围。`crawl` 默认仅 `cs.*`；复现 all-subject vault 需要显式 categories。`index --skip-embeddings` 只建关键词索引，不能充当 embedding novelty 完整配置。构库和 decomposition 有显著网络、模型调用与存储开销，不能作为普通 skill 调用的隐式准备步骤。

HF 页面在核查时显示 viewer 时间戳解析错误；这只说明 preview 的自动类型推断失败，不足以证明原数据文件损坏。读取时固定 revision，并检查日期、唯一 ID、split、字段类型及样本内容。

## 5. 最小推理与评价

准备一个只含问题和 challenge 的 `problem.txt`，并先取得它在本地 vault 中对应的数字 paper ID。将下例所有 `<PID>` 替换为该 ID；target 的正文和参考方案不得进入 ideation agent：

```bash
python scripts/run_ideation.py --problem-file problem.txt --problem-id pid<PID> --query-paper-id <PID> --run-dir runs/base/runs
python scripts/evaluate.py runs/base/runs/<timestamp>_pid<PID> --target-paper-id <PID>
python scripts/evaluate.py runs/base/runs/<timestamp>_pid<PID> --target-paper-id <PID> --reference-report <label>/report.json
python scripts/compute_novelty_aspects.py runs/base --out runs/base/novelty_aspects.jsonl --denominator 1 --model Qwen3.6-27B
```

`<timestamp>_pid<PID>` 采用实际生成的目录名。显式传入 target ID 可避免默认 slug 无法被 evaluator 解析。若使用 arXiv ID，先核对 `evaluate.py --help` 的 `--target-arxiv` 映射，不能猜测 vault 数字 ID。

`compute_novelty_aspects.py` 扫描 `<system-root>/runs/*/outputs/report.json`，所以上例是 `runs/base/runs` 布局。单题 smoke check 的分母是 1；完整实验改为预先冻结的 target 总数（如 paper277 或 public272），失败项也计入。每个系统使用独立 `--out`，避免共享默认输出导致按 paper ID 跳过别的系统记录。

先完成一个 target 的端到端验证：有角色日志、`gaps.md`、`candidates.md`、`report.json`、已读引用与 `evaluation/evaluation.json`，再扩展样本。Reference report 只允许进入离线评价，不给 ideation agent 读取。上游 aggregator 与论文 Table 1 公式不同，处理方式见 [evaluation.md](evaluation.md)。

## 6. 训练配置记录

先生成参考产物（gap_finder → innovator → report_writer），再构角色训练集；以下展示一个角色的入口，另外两角色同理。

```bash
python scripts/build_references.py gap_finder
python -m ideascientist.training.datasets.gap_finder
python scripts/train_role.py gap_finder
```

论文 E.1：每角色 LoRA rank32 / alpha64 / dropout0；AdamW LR5e-6、weight_decay0.01、clip1.0；bfloat16、TP8；64 prompts ×8 generations =512 rollouts，训练 batch256；ratio clip[0.2,0.28]、无 KL reward；异步 GRPO 最大 staleness1。

| 角色 | 序列长度 | 训练上限 | 论文选中 step |
|---|---:|---|---:|
| gap_finder | 26,624 | 2 epochs / 800 steps | 380 |
| innovator | 30,720 | 1 epoch / 600 steps | 310 |
| report_writer | 49,152 | 2 epochs / 600 steps | 194 |

论文每角色用 **40×8 =320 H100**，32 节点优化、8 节点 rollout；核查到 public gap_finder YAML 是 **8×8 =64 GPU** 且 colocated generation。公开配置不应直接称作原拓扑精确复现。减少资源可作 adaptation，但要记录配置变化并重新验证。

## 7. 复现报告最低内容

保存代码 SHA、数据 revision 与 split ID manifest、模型/adapter版本、完整依赖版本、数据库/index指纹、cutoff、逐角色预算、端点配置、种子、逐题原始输出、失败原因、judge原响应、指标映射和固定分母。对每一项写“已取得 / 已核对 / 未取得 / 未执行”。论文报告分数可以引用；没有实际运行得到的本地分数不能填成复现结果。
