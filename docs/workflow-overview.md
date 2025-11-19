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
| `coverup.testrunner` | 集成 SlipCover，执行整套及单测覆盖率评估。 |
| `coverup.llm` | 统一的 LLM 客户端（OpenAI/Anthropic/Bedrock/Ollama），负责工具调用与重试/计费逻辑。 |
| `coverup.prompt.*` | 针对不同模型的提示模板与工具函数。 |
| `coverup.codeinfo` | 符号解析与代码摘录的静态分析工具集合。 |
| `coverup.utils` | 格式化辅助、异步子进程封装、覆盖率汇总函数。 |

## 流程摘要

1. 用户运行 `coverup --package-dir src/pkg --tests tests`。
2. 通过 SlipCover 采集基线覆盖率 → 获得 JSON 覆盖率映射。
3. 基于 AST 的分段逻辑识别欠覆盖单元。
4. 针对每个代码段：
   - 向 LLM 提供上下文与缺失覆盖信息。
   - 可选调用 `get_info` 获取额外符号信息。
   - 在 SlipCover 下验证候选测试，若提升了覆盖率则接受。
5. 接受的测试保存在 `tests/test_coverup_*.py` 中，进度异步管理。
6. 重新计算最终覆盖率，更新报告与检查点。

上述流程保证 CoverUp 能迭代提升测试套件，同时将 LLM 建议扎根于精确的静态结构与真实的覆盖率度量之上。
