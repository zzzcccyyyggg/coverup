# CoverUp 项目架构文档

> LLM 驱动的覆盖率引导测试生成框架（FSE 2025），支持 Python / Go / Rust 三种语言。
> 版本：v0.6.3 | 组织：UMass PLASMA Lab

---

## 一、项目总览

CoverUp 通过大语言模型（LLM）自动为源代码生成测试，以提高代码覆盖率。核心循环：

```
发现未覆盖代码段 → 构造 Prompt → LLM 生成测试 → 编译/运行/度量覆盖率 → 修复失败 → 持久化成功测试
```

### 关键特性

| 特性 | 说明 |
|------|------|
| 多语言支持 | Python（SlipCover）、Go（go test -coverprofile）、Rust（cargo llvm-cov） |
| 多模型支持 | OpenAI GPT-4o、Anthropic Claude、AWS Bedrock、Ollama、DeepSeek |
| Agent 增强 | ReflectiveMemory / UCBPlanner / RepairOrchestrator / CoverageBlocker |
| 消融实验 | 5 种变体（full / no_memory / no_repair / no_planner / baseline） |

---

## 二、目录结构

```
coverup/
├── pyproject.toml              # 构建配置 & 依赖声明（入口点: coverup = coverup.coverup:main）
├── setup.py                    # PyPI 发布辅助（动态版本 & README）
├── README.md                   # 项目说明文档
├── test-modules.txt            # 生成测试可能需要的可选依赖
│
├── src/                        # ========== 源代码 ==========
│   ├── coverup/                # 【核心包】
│   │   ├── coverup.py          # CLI 入口 & 主调度循环
│   │   ├── segment.py          # 代码段提取（从覆盖率缺口）
│   │   ├── codeinfo.py         # Python 静态分析（AST / 符号 / 导入）
│   │   ├── go_codeinfo.py      # Go 静态分析（tree-sitter + go doc）
│   │   ├── rust_codeinfo.py    # Rust 静态分析（tree-sitter + stdlib）
│   │   ├── testrunner.py       # 覆盖率度量（SlipCover 集成）
│   │   ├── llm.py              # LLM 客户端（litellm 统一接口 + 速率限制 + 成本计算）
│   │   ├── diagnostic_ir.py    # 语言无关的错误分类（DiagnosticIR）
│   │   ├── python_support.py   # 运行时依赖检测 & pip 安装
│   │   ├── utils.py            # 格式化、子进程、覆盖率聚合
│   │   ├── logreader.py        # 日志解析
│   │   ├── version.py          # 版本号 v0.6.3
│   │   │
│   │   ├── agents/             # 【Agent 模块】
│   │   │   ├── memory.py       # ReflectiveMemory — UCB×时间衰减的修复经验库
│   │   │   ├── planner.py      # UCBPlanner — 多臂老虎机批次调度器
│   │   │   ├── repair.py       # RepairOrchestrator — 二阶段修复（确定性工具→LLM回退）
│   │   │   ├── blocker.py      # CoverageBlocker — 守卫提取 + 变量溯源 → 结构化提示
│   │   │   └── trace.py        # TraceLogger — 结构化 JSONL 追踪日志
│   │   │
│   │   ├── languages/          # 【语言后端】
│   │   │   ├── base.py         # 抽象基类接口
│   │   │   ├── python_backend.py  # Python: SlipCover + pytest
│   │   │   ├── go_backend.py      # Go: go test + goimports/gofmt
│   │   │   └── rust_backend.py    # Rust: cargo llvm-cov + rustfmt
│   │   │
│   │   └── prompt/             # 【Prompt 模板】
│   │       ├── prompter.py     # 基类接口: initial_prompt / error_prompt / get_info
│   │       ├── gpt_v1.py       # GPT-4 基础 Prompt
│   │       ├── gpt_v2.py       # 增强 Prompt（覆盖率 + get_info + 错误上下文）
│   │       ├── gpt_v2_ablated.py  # 消融变体（去覆盖率/get_info/修复/全去）
│   │       ├── claude.py       # Claude 专用 Prompt
│   │       ├── gpt_go_v1.py    # Go 专用（分支推断 + 接口/错误/协程模式）
│   │       └── gpt_rust_v1.py  # Rust 专用（17条约束 + trait/所有权/unsafe 指导）
│   │
│   ├── click/                  # 【外部基准】Click CLI 框架（gitignored）
│   ├── cobra/                  # 【外部基准】Cobra CLI 框架 Go（gitignored）
│   ├── flask/                  # 【外部基准】Flask Web 框架（gitignored）
│   └── validator/              # 【外部基准】数据验证器 Go（gitignored）
│
├── experiments/                # ========== 实验（与代码分离） ==========
│   ├── scripts/                # 实验运行与分析脚本
│   │   ├── experiment_config.yaml  # 实验矩阵（9项目×5变体×3种子=135次运行）
│   │   ├── run_experiments.py      # 主实验运行器
│   │   ├── analyze_log.py          # 日志分析
│   │   └── analyze_results.py      # 结果后处理
│   ├── baselines/              # 覆盖率基线快照
│   │   ├── slipcover.json      # Flask 基线覆盖率
│   │   └── slipcover_click.json  # Click 基线覆盖率
│   ├── docs/                   # 实验文档
│   │   ├── experiment_design.md    # 实验设计方案
│   │   └── experiment-results.md   # 实验结果分析
│   ├── results/                # 实验结果输出（gitignored）
│   └── logs/                   # 实验日志输出（gitignored）
│
├── paper/                      # ========== 论文材料 ==========
│   ├── coverup.txt             # 论文正文（文本版）
│   ├── coverup.pdf             # 论文正文（PDF 版）
│   ├── paper-outline.md        # 论文大纲
│   ├── paper-roadmap.md        # 论文路线图
│   └── paper-comparison.md     # 相关工作对比
│
├── docs/                       # ========== 项目设计文档 ==========
│   ├── system-summary.md       # Agent 系统总结
│   ├── agent-architecture.md   # Agent 架构设计
│   ├── workflow-overview.md    # 工作流概览
│   ├── testing-guide.md        # 测试指南
│   ├── go_generation_updates.md  # Go 生成改进记录
│   ├── rust_adaptation.md      # Rust 适配文档
│   └── next-language-recommendation.md  # 下一语言扩展建议
│
├── tests/                      # ========== 生成的测试（gitignored） ==========
├── tests-click/                # Click 专用测试（gitignored）
└── images/                     # Logo & 对比图表
```

---

## 三、核心执行流程

```
main() [coverup.py]
 │
 ├─ 1. 解析 CLI 参数
 ├─ 2. 加载语言后端 (Python/Go/Rust)
 ├─ 3. 初始化 LLM 客户端 (litellm)
 ├─ 4. 加载/创建检查点状态
 ├─ 5. 度量基线覆盖率
 │
 ├─ 6. 发现未覆盖代码段 [segment.py]
 │     └─ 按优先级排序（覆盖率缺口大小、复杂度）
 │
 ├─ 7. 初始化 Agent 模块
 │     ├─ ReflectiveMemory  [agents/memory.py]
 │     ├─ UCBPlanner         [agents/planner.py]
 │     ├─ RepairOrchestrator [agents/repair.py]
 │     └─ CoverageBlocker    [agents/blocker.py]
 │
 ├─ 8. 异步生成循环（按批次）
 │     for batch in planner.select_batch(k):
 │       for segment in batch:
 │         ├─ 构造 Prompt（源码 + 覆盖率信息 + 记忆提示 + 阻塞器提示）
 │         ├─ LLM 生成测试代码（可调用 get_info 工具）
 │         ├─ 编译 & 运行测试
 │         ├─ 度量覆盖率增量
 │         ├─ 失败时：DiagnosticIR 分类 → 修复尝试
 │         │   ├─ Phase 1: 确定性工具修复
 │         │   └─ Phase 2: LLM 回退（含记忆提示）
 │         ├─ 记录结果 (memory.record / planner.update / trace.log)
 │         └─ 成功且覆盖率增加 → 保存测试文件
 │
 └─ 9. 后处理
       ├─ 重新度量全套件覆盖率
       ├─ 打印汇总（初始→最终覆盖率、成本、测试统计）
       └─ 保存检查点
```

---

## 四、Agent 协作机制

```
┌─────────────────────────────────────────────────────────┐
│                     UCBPlanner (P2/P4)                   │
│  多臂老虎机调度：选择高期望值代码段批次                    │
│  - 平台检测（覆盖率不再增长时切换策略）                    │
│  - 缺口复杂度评估                                        │
│  CLI: --no-agent-planner                                 │
└────────────────────┬────────────────────────────────────┘
                     │ 选择批次
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Prompt 构造阶段                               │
│                                                          │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ ReflectiveMemory(P1)│  │ CoverageBlocker (P5)      │  │
│  │ UCB×时间衰减排序     │  │ 守卫提取+变量溯源         │  │
│  │ 注入成功修复经验     │  │ "行Y因guard(x>0)未覆盖"  │  │
│  │ --no-agent-memory   │  │ --no-agent-blocker        │  │
│  └─────────────────────┘  └───────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                     │
                     ▼
              LLM 生成测试
                     │
                     ▼ 失败时
┌──────────────────────────────────────────────────────────┐
│             RepairOrchestrator (P3)                       │
│  Phase 1: 确定性工具修复（7个内置修复器）                  │
│    - import 修复、类型转换、可见性、panic 防护等           │
│  Phase 2: LLM 回退 + Memory 提示                         │
│  CLI: --no-agent-repair                                  │
└──────────────────────────────────────────────────────────┘
```

---

## 五、实验运行方式

### 5.1 单次运行（日常使用）

```bash
# 激活环境
source .venv/bin/activate

# Python 项目 — 为 Flask 生成测试
coverup --package-dir src/flask --tests tests --model gpt-4o

# Go 项目
coverup --language go --package-dir src/cobra --model gpt-4o

# Rust 项目
coverup --language rust --package-dir src/similar --prompt gpt-rust-v1 --model gpt-4o

# Dry run（不调用 LLM，仅查看计划）
coverup --package-dir src/flask --dry-run

# 从检查点恢复
coverup --package-dir src/flask --checkpoint flask_progress.pkl
```

### 5.2 常用 CLI 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--package-dir` | 必填 | 被测源码目录 |
| `--tests-dir` | 自动发现 | 测试输出目录 |
| `--language` | python | 语言：python / go / rust |
| `--model` | 自动检测 | LLM 模型名称 |
| `--prompt` | gpt-v2 | Prompt 族：gpt-v1 / gpt-v2 / claude / gpt-go-v1 / gpt-rust-v1 |
| `--max-attempts` | 3 | 每段最大重试次数 |
| `--line-limit` | 50 | 每段目标行数 |
| `--rate-limit` | 无 | Token/分钟限制 |
| `--checkpoint` | 无 | 检查点文件路径 |
| `--prefix` | coverup | 生成文件前缀 |
| `--repeat-tests` | 5 | 抖动检测运行次数 |
| `--log-file` | coverup-log | 日志文件名 |
| `--no-agent-memory` | — | 禁用 ReflectiveMemory |
| `--no-agent-planner` | — | 禁用 UCBPlanner |
| `--no-agent-repair` | — | 禁用 RepairOrchestrator |
| `--no-agent-blocker` | — | 禁用 CoverageBlocker |
| `--trace-log` | — | 启用 JSONL 追踪日志 |
| `--dry-run` | — | 仅规划不调用 LLM |
| `--install-missing-modules` | — | 自动安装缺失的 Python 包 |

### 5.3 批量实验矩阵

实验配置文件：[experiments/scripts/experiment_config.yaml](experiments/scripts/experiment_config.yaml)

```
矩阵: 9 个项目 × 5 种变体 × 3 个随机种子 = 135 次运行

项目:
  Rust (3): similar, semver, strsim-rs
  Python (3): flask, click, pydantic-core
  Go (3): cobra, logrus, gjson

变体:
  1. full          — 所有 Agent（Memory + Repair + Planner）
  2. no_memory     — 禁用 ReflectiveMemory
  3. no_repair     — 禁用 RepairOrchestrator
  4. no_planner    — 禁用 UCBPlanner（使用轮询）
  5. baseline      — 原版 CoverUp（无 Agent）

种子: [42, 123, 456]
模型: deepseek/deepseek-coder (via litellm)
```

运行实验：

```bash
python experiments/scripts/run_experiments.py     # 运行完整实验矩阵
python experiments/scripts/analyze_log.py         # 分析日志
python experiments/scripts/analyze_results.py     # 后处理结果
```

输出位置：
- 结果: `experiments/results/`
- 日志: `experiments/logs/`
- 汇总: `experiments/summary.csv`

---

## 六、依赖清单

### 核心运行时

| 包 | 版本 | 用途 |
|----|------|------|
| slipcover | ≥1.0.13 | Python 精确行/分支覆盖率 |
| pytest-cleanslate | ≥1.0.6 | 测试隔离 |
| litellm | ≥1.33.1 | 统一 LLM 客户端 |
| openai | latest | OpenAI API |
| aiolimiter | latest | 异步速率限制 |
| tqdm | latest | 进度条 |
| tiktoken | latest | Token 计数 |
| tree-sitter + tree-sitter-languages | latest | Go/Rust 静态分析（可选） |

### 构建系统

```toml
[build-system]
requires = ["setuptools>61", "wheel", "tomli; python_version < '3.11'"]
build-backend = "setuptools.build_meta"
```

### 开发安装

```bash
pip install -e ".[dev]"
pip install tree-sitter tree-sitter-languages  # Go/Rust 支持
```

---

## 七、版本管理建议

### 关键文件变更影响

| 修改对象 | 影响范围 | 注意事项 |
|----------|----------|----------|
| `coverup.py` | 全局执行流程 | 主入口，修改需全面测试 |
| `agents/*.py` | Agent 行为 | 每个 Agent 可独立禁用测试 |
| `languages/*.py` | 特定语言后端 | 仅影响对应语言的测试生成 |
| `prompt/*.py` | LLM 输出质量 | 需配合实际生成结果验证 |
| `segment.py` / `codeinfo.py` | 代码分析 | 影响所有 Python 项目的段发现 |
| `llm.py` | 模型交互 | 影响所有语言的 LLM 调用 |
| `experiment_config.yaml` | 实验设置 | 仅影响批量实验 |

### 建议的分支策略

```
main              ← 稳定版本
├── dev           ← 开发整合
│   ├── feat/*    ← 新功能（如新语言支持）
│   ├── agent/*   ← Agent 模块改进
│   ├── prompt/*  ← Prompt 优化
│   └── exp/*     ← 实验配置调整
└── release/*     ← 发布版本
```

### 快速验证命令

```bash
# 运行 codeinfo 单元测试
pytest tests/test_codeinfo.py -v

# Dry run 验证基本流程
coverup --package-dir src/flask --dry-run

# 检查版本
python -c "from coverup.version import __version__; print(__version__)"
```
