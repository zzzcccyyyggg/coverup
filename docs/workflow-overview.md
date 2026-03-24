# CoverUp 工作流程概览

本文档介绍 CoverUp 如何编排基于覆盖率的测试生成流程、如何采集覆盖率数据，以及静态分析在其中承担的角色。

## 整体流程

1. **CLI 初始化**（`coverup.coverup.main`）
   - 解析命令行参数（`parse_args`）。
   - 解析源码与测试目录，配置 `PYTHONPATH` 以支持源码内导入。
   - 构建选定的 LLM 提示器（`Prompter`）与对话客户端（`llm.Chatter`）。
   - 初始化日志、速率限制与可选的检查点状态（`State`）。

2. **基线覆盖率测量**
   - 使用 `measure_suite_coverage`（SlipCover + pytest）执行现有测试套件。
   - 收集 JSON 覆盖率元数据：每个文件的执行/缺失行与分支。
   - 构建按优先级排序的欠覆盖代码段工作列表（`segment.get_missing_coverage`）。

3. **LLM 驱动的测试生成循环**
   - 针对每个代码段，由提示器生成定制提示（`Prompter.initial_prompt`）。
   - 通过 `llm.Chatter.chat` 与 LLM 交互，可按需调用 `Prompter.get_info` 等工具函数补充静态上下文。
   - 提取候选 pytest 测试代码块（`extract_python`）。
   - 如允许，自动安装或导入缺失的运行时依赖。

4. **候选测试评估**
   - 将候选测试写入测试目录的临时文件。
   - 通过 `measure_test_coverage` 在 SlipCover 下重复执行该测试（异步封装 `slipcover -m pytest`）。
   - 利用 `State` 与 `Progress` 记录结果（成功/失败/无效/重试）。
   - 将成功测试持久化到按序号命名的文件（`test_file_path`、`new_test_file`），并可选保存覆盖率快照。
   - 对失败或覆盖不足的候选测试，通过 `error_prompt`、`missing_coverage_prompt` 回馈给 LLM 迭代修正。

5. **后处理**
   - 可选地清理测试套件以隔离污染或失败的测试（`check_whole_suite`）。
   - 使用 SlipCover 重新跑完整测试套件以报告最终覆盖率提升。
   - 保存检查点并提示可能缺失的第三方依赖。

## 覆盖率采集

CoverUp 使用 [SlipCover](https://github.com/plasma-umass/slipcover) 精确收集行与分支覆盖率：

- **整套测试覆盖率**（`testrunner.measure_suite_coverage`）
  - 调用 `python -m slipcover --json --out <tmp> -m pytest …`。
  - 支持分支覆盖、pytest 附加参数与测试隔离等选项。
  - 返回 SlipCover 生成的 JSON 文档，包含各文件的执行数据与整体覆盖率。
  - 基于 `--continue-on-failure` 控制 pytest 非零退出码（失败/不稳定测试）的处理方式。

- **单个测试覆盖率**（`testrunner.measure_test_coverage`）
  - 将生成的测试落地至测试目录的临时文件。
  - 以静默模式运行 SlipCover + pytest，降低令牌消耗。
  - 解析 JSON 报告，计算候选测试触达的行与分支。
  - 根据 `--repeat-tests` 设置重复执行以筛除不稳定测试。

覆盖率 JSON 结构如下：

```json
{
  "files": {
    "/abs/path/to/module.py": {
      "executed_lines": [...],
      "missing_lines": [...],
      "executed_branches": [[from, to], ...],
      "missing_branches": [[from, to], ...]
    }
  },
  "summary": {"percent_covered": 94.4}
}
```

`utils.summary_coverage` 用于筛选并格式化这些数据，而 `segment.CodeSegment` 则按代码段比较覆盖率增量，以决定是否接受生成的测试。

## 静态分析职责

静态分析支撑了整个流程的多个环节：

- **代码段提取（`segment.get_missing_coverage`）**
  - 使用 `ast` 解析模块（`codeinfo.parse_file`）。
  - 将缺失的行/分支映射到最小的封闭函数、方法或类定义。
  - 生成 `CodeSegment` 对象，封装 AST 上下文、缺失/已执行行、相关导入与代码摘录。

- **上下文提示（`CodeSegment.get_excerpt`）**
  - 构建带行号的精简源码片段，并补全关键导入，帮助 LLM 准确理解场景。

- **符号查询（`codeinfo.get_info`）**
  - 暴露 `get_info` 工具函数，供 LLM 在对话中即时调用。
  - 通过 AST 遍历与包级导入解析，定位类/函数定义，甚至可跨模块追踪重导出符号。
  - 使用 `_summarize` 精简目标定义，结合 `get_global_imports` 自动补全所需导入。

- **导入推断（`CodeSegment.imports`）**
  - 收集模块级导入，确保片段可独立编译，减少 LLM 的猜测空间。

这些分析提供了精确的结构化上下文，使 LLM 能生成正确、针对性强的测试，同时降低幻觉风险。

## 核心模块

| 模块 | 职责 |
| --- | --- |
| `coverup.coverup` | CLI 入口、调度、检查点管理、异步任务以及日志。 |
| `coverup.segment` | 根据 AST 分割欠覆盖代码并提取上下文。 |
| `coverup.testrunner` | 集成 SlipCover，执行整套及单测覆盖率评估（Python）。 |
| `coverup.llm` | 统一的 LLM 客户端（OpenAI/Anthropic/Bedrock/Ollama），负责工具调用与重试/计费逻辑。 |
| `coverup.prompt.*` | 针对不同模型/语言的提示模板与工具函数。 |
| `coverup.codeinfo` | Python 符号解析与代码摘录的静态分析工具集合。 |
| `coverup.go_codeinfo` | **Go 静态分析引擎**：符号查询（tree-sitter + `go doc`）、分支覆盖推断、接收者类型提取。 |
| `coverup.rust_codeinfo` | **Rust 静态分析引擎**：符号查询（tree-sitter，支持 fn/struct/enum/trait/impl::method/const/static/mod）、分支推断（if/if_let/match）、标准库文档（40+ 常用类型）。 |
| `coverup.diagnostic_ir` | **诊断中间表示**：统一三种语言的编译/运行错误为 `DiagnosticIR` 结构体。 |
| `coverup.agents.memory` | **ReflectiveMemory**：成功加权食谱库，基于 UCB×recency 排序，注入正面处方。 |
| `coverup.agents.planner` | **UCBPlanner**：多臂赌博机调度器，`select_batch(k)` 批次波次选择高价值段。 |
| `coverup.agents.repair` | **RepairOrchestrator**：两阶段修复（确定性工具→LLM 回退），含 cargo check JSON 自动修复。 |
| `coverup.agents.trace` | **TraceLogger**：JSONL 结构化日志（已实现，待接入主循环）。 |
| `coverup.languages.python_backend` | Python 后端：SlipCover + pytest 覆盖率测量与测试管理。 |
| `coverup.languages.go_backend` | Go 后端：`go test -coverprofile` + tree-sitter 分段 + 分支推断。临时文件使用 `_test.go` 后缀；自动发现 `goimports`。 |
| `coverup.languages.rust_backend` | **Rust 后端**：`cargo llvm-cov --json` 覆盖率采集 + tree-sitter 分段 + 集成测试策略（tests/ 目录）+ `rustfmt` 格式化。 |
| `coverup.utils` | 格式化辅助、异步子进程封装、覆盖率汇总函数。 |

## Go 语言支持

CoverUp 现在对 Go 提供深度支持，与 Python 后端能力对齐：

### Go 流程概览

1. 用户运行 `coverup --language go --package-dir /path/to/go/module`。
2. 通过 `go test -coverprofile` 采集基线覆盖率。
3. `go_backend` 使用 tree-sitter 解析 Go AST，识别欠覆盖的函数/方法/类型/变量。
4. `go_codeinfo.infer_branches()` 分析控制流（if/else、switch/case、select）推断分支覆盖。
5. 针对每个代码段：
   - `gpt_go_v1` Prompt 包含行/分支标注、约束、动态 Go 特性指导。
   - LLM 可调用 `get_info` 工具函数查询 struct/interface/函数定义。
   - 生成的 `_test.go` 文件经 `goimports` 格式化后由 `go test` 验证。
   - 失败时清洗错误信息后回馈 LLM 修正；缺失模块自动 `go mod tidy` 并重试。
6. 成功的测试保存为 `coverup_NNN_test.go`，带覆盖率元数据注释。
7. 重新测量最终覆盖率。

### Go/Rust vs Python 功能对比

| 功能 | Python | Go | Rust |
|------|--------|-----|------|
| 覆盖率工具 | SlipCover | `go test -coverprofile` | `cargo llvm-cov --json` |
| 分支覆盖 | 原生支持 | 通过控制流分析推断 | 通过控制流分析推断 |
| 代码分段 | Python AST | tree-sitter | tree-sitter |
| 符号查询 (`get_info`) | `codeinfo.py` (AST 遍历) | `go_codeinfo.py` (tree-sitter + `go doc`) | `rust_codeinfo.py` (tree-sitter + 内置 std 文档) |
| 测试框架 | pytest | Go `testing` package | Rust `#[test]` + `cargo test` |
| 测试策略 | pytest 文件 | 同包 `_test.go` | 集成测试 `tests/` 目录 |
| Prompt 模板 | `gpt_v2.py` / `claude.py` | `gpt_go_v1.py` | `gpt_rust_v1.py` |
| 错误清洗 | `clean_error()` | `format_test_error()` | `format_test_error()` |
| 依赖管理 | `pip install` | `go mod tidy` + 自动重试 | `cargo` 自动依赖解析 |
| 代码格式化 | — | `goimports` / `gofmt`（自动发现） | `rustfmt`（自动 fallback） |
| 动态指导 | — | interface/error/goroutine/context 等 | trait/Result/Option/async/lifetime/unsafe/generics/serde 等 |
| Prompt 约束 | 基础约束 | 未使用变量/模板 panic 防护 | 17 条约束（`#[test]`/unsafe/泛型/错误处理等） |
| 标准库文档 | — | `go doc` 命令 | 内置 40+ 常用类型文档 |

### Go 适配验证结果（src/cobra）

| 指标 | 值 |
|------|-----|
| 基线覆盖率 | 90.9% |
| 最终覆盖率 | 97.7% (+6.8pp) |
| 成功测试 (G) | 87 |
| 失败测试 (F) | 66 |
| 无用测试 (U) | 1 |
| 模型 | deepseek/deepseek-coder |
| 成本 | ~$0.23 |

## 流程摘要

### Python 流程
1. 用户运行 `coverup --package-dir src/pkg --tests tests`。
2. 通过 SlipCover 采集基线覆盖率 → 获得 JSON 覆盖率映射。
3. 基于 AST 的分段逻辑识别欠覆盖单元。
4. 针对每个代码段：
   - 向 LLM 提供上下文与缺失覆盖信息。
   - 可选调用 `get_info` 获取额外符号信息。
   - 在 SlipCover 下验证候选测试，若提升了覆盖率则接受。
5. 接受的测试保存在 `tests/test_coverup_*.py` 中，进度异步管理。
6. 重新计算最终覆盖率，更新报告与检查点。

### Go 流程
1. 用户运行 `coverup --language go --package-dir /path/to/module`。
2. 通过 `go test ./... -coverprofile` 采集基线覆盖率。
3. tree-sitter 解析 + 控制流分析识别欠覆盖单元与分支。
4. 针对每个代码段：
   - Prompt 包含行/分支标注、接收者类型上下文、动态指导。
   - LLM 可调用 `get_info` 查询符号定义。
   - `go test` 验证候选测试，失败时清洗错误后回馈。
5. 成功的测试保存为 `coverup_NNN_test.go`。
6. 重新计算最终覆盖率。

### Rust 流程
1. 用户运行 `coverup --language rust --package-dir /path/to/crate`。
2. 通过 `cargo llvm-cov --json` 采集基线覆盖率（需要 `llvm-tools-preview` + `cargo-llvm-cov`）。
3. tree-sitter 解析 Rust AST，识别欠覆盖的 fn/struct/enum/trait/impl/const/static/mod。
4. `rust_codeinfo.infer_branches()` 分析控制流（if/if_let/match）推断分支覆盖。
5. 针对每个代码段：
   - `gpt_rust_v1` Prompt 包含行/分支标注、17 条 Rust 专属约束、动态特性指导。
   - LLM 可调用 `get_info` 工具函数查询符号定义与标准库文档。
   - 生成的测试文件放入 `tests/` 目录（集成测试策略，使用 `use <crate>::*`）。
   - 经 `rustfmt` 格式化后由 `cargo test` 验证。
   - 失败时清洗错误信息后回馈 LLM 修正。
6. 成功的测试保存为 `tests/coverup_NNN.rs`。
7. 重新计算最终覆盖率。

上述流程保证 CoverUp 能迭代提升测试套件，同时将 LLM 建议扎根于精确的静态结构与真实的覆盖率度量之上。

## CoverAgent-ML 智能体层

CoverUp 的基础流程之上增加了可选的**自适应智能体层**（CoverAgent-ML），通过 `--no-agent-*` CLI 标志控制，详见 [agent-architecture.md](agent-architecture.md)。

### 组件概览

| 组件 | CLI 禁用标志 | 职责 |
|------|------------|------|
| **ReflectiveMemory** | `--no-agent-memory` | 基于成功率的食谱库，向 prompt 注入正面修复处方 |
| **UCBPlanner** | `--no-agent-planner` | 多臂赌博机调度器，选择高价值代码段优先处理 |
| **RepairOrchestrator** | `--no-agent-repair` | 编译失败时先用确定性工具修复，再回退 LLM |
| **TraceLogger** | — | JSONL 结构化追踪日志（已实现，待接入） |

### 数据流

1. Planner 的 `select_batch(k)` 选择本波 top-k 段（替代一次性全量调度）
2. Memory 的 `format_for_prompt()` 向初始 prompt 注入 top-k 成功食谱
3. 编译失败后 → `classify_error()` → `DiagnosticIR` → Repair 尝试工具修复
4. 每次尝试结束后 → `memory.record()` + `planner.update()` 闭环更新

### 实验结果（`similar` crate, Rust）

| 配置 | 覆盖率 | G | F | 总调用 | 费用 |
|------|--------|---|---|--------|------|
| Agent v2 (全部启用) | 92.5% | 23 | 110 | 148 | ~$0.35 |
| Baseline (全部禁用) | 90.9% | 31 | 173 | 210 | ~$0.39 |
