# CoverAgent-ML 智能体架构总览

> 版本: v3 (P0-P5 全部实现)  ·  最后更新: 2026-02-17

---

## 1. 设计目标

CoverAgent-ML 在 CoverUp（基于 LLM 的覆盖率驱动测试生成框架）之上增加了一层**自适应智能体层**，目标是：

1. **提高覆盖率上限** — 让同等 LLM 调用次数产出更多有效代码行覆盖
2. **提升效率** — 减少无效 LLM 调用（Failed / Useless），降低 API 成本
3. **跨语言通用** — Rust / Python / Go 共享同一套智能体框架
4. **消融友好** — 每个组件均可通过 CLI 标志独立禁用，方便 A/B 实验

---

## 2. 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                      coverup.py 主循环                    │
│                                                          │
│  ┌────────────┐  select_batch(k)  ┌──────────────────┐  │
│  │ UCBPlanner │◄──────────────────│   Wave 调度器     │  │
│  │  (P2/P4)   │──────────────────►│ (并发=k segments) │  │
│  └────────────┘  top-k arm IDs    └──────┬───────────┘  │
│                                          │               │
│                        ┌─────────────────▼────────┐      │
│                        │  单 segment 处理管线       │      │
│                        │                           │      │
│  ┌────────────────┐    │  1. Memory → prompt 注入   │      │
│  │ReflectiveMemory│◄───│  2. LLM 生成测试代码       │      │
│  │    (P1)        │────│  3. backend 编译 & 运行     │      │
│  └────────────────┘    │  4. 失败 → Repair → 重试   │      │
│                        │  5. record() + update()    │      │
│  ┌────────────────┐    │                           │      │
│  │RepairOrchestra-│◄───│  Phase 1: 确定性工具修复   │      │
│  │  tor (P3)      │────│  Phase 2: LLM 回退 + hint │      │
│  └────────────────┘    └───────────────────────────┘      │
│                                                          │
│  ┌────────────┐                                          │
│  │TraceLogger │  每次尝试写 JSONL 行 (P0, 尚未接入主循环)  │
│  │   (P0)     │                                          │
│  └────────────┘                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 四大组件详解

### 3.1 ReflectiveMemory — 食谱库（P1）

**文件**: `src/coverup/agents/memory.py` (412 行)

#### 核心思想

不再统计"哪些错误最常出现"（频率表），而是跟踪"哪些修复动作对哪些诊断签名有效"（食谱库）。注入 LLM 的提示是**正面处方**（"Do: use `crate::module::Struct` 格式"），而非负面警告（"Avoid: 不要使用错误的导入"）。

#### 数据结构

| 类型 | 说明 |
|------|------|
| `Recipe` | 单个修复动作统计：`action_name`, `success_count`, `try_count`, `total_cost_sec`, `total_delta_cov`, `last_seen_ts` |
| `SignatureEntry` | 按四元组 `(language, phase, error_category, signature)` 索引，持有多个 `Recipe` |
| `ReflectiveMemory` | 线程安全主类，内部 `Dict[key, SignatureEntry]` |

#### 签名提取

将 `DiagnosticIR` 的 `error_code` + 归一化消息（去数字 / 去路径 / 去具体符号名）组合为指纹，确保同类错误聚合。

#### 排序公式

$$\text{score} = \text{UCB}\bigl(\text{success\_rate}\bigr) \times \bigl(0.3 + 0.7 \times \text{recency}\bigr)$$

- **UCB 探索项**: $\sqrt{\frac{2 \ln N}{n}}$，$N$ 为全局尝试数，$n$ 为该 recipe 尝试数
- **Recency 衰减**: 半衰期 600 秒，`recency = exp(-0.693 × Δt / 600)`

#### 冷启动守卫

`try_count < 3` 的 recipe **不会注入 prompt**，避免基于不充分统计的误导。

#### 预置处方模板

覆盖三种语言的常见错误类别（import / type / visibility / ownership / assertion / panic），共 12 条预置 recipe，`try_count=3, success_count=2`，确保初始就有可用建议。

#### 接口

| 方法 | 调用时机 | 说明 |
|------|---------|------|
| `record(ir, action, succeeded)` | 每次尝试完成后 | 更新对应签名的 recipe 统计 |
| `format_for_prompt(language, max_lessons)` | 构建初始 prompt 时 | 返回 top-k 正面处方字符串 |
| `format_entry_for_error(ir)` | 工具修复失败、回退 LLM 时 | 为特定错误类别返回针对性建议 |
| `query(language, error_category, max_results)` | 内部方法 | 按 UCB×recency 排序返回最佳 recipe |

---

### 3.2 UCBPlanner — 多臂赌博机调度器（P2 + P4）

**文件**: `src/coverup/agents/planner.py` (337 行)

#### 核心思想

将每个代码段（segment）视为**赌博机的一个臂（arm）**，通过 UCB（Upper Confidence Bound）算法平衡**探索**（尝试未知段）与**利用**（优先高回报段），避免在低价值段上浪费 LLM 调用。

#### 臂（Arm）统计

| 字段 | 说明 |
|------|------|
| `pulls` | 总尝试次数 |
| `successes` | 成功产生覆盖率增益的次数 |
| `compiles` | 编译通过的次数（含无增益） |
| `failures` | 编译/运行失败次数 |
| `total_gain` | 成功时的累计覆盖率增益 |
| `consecutive_useless` | 连续"编译成功但无增益"次数 |
| `frozen` | 是否冻结（plateau ≥ 3） |
| `gap_complexity` | 基于缺失行数的复杂度因子（P4） |

#### 评分公式

$$\text{score} = \frac{\text{UCB}(p\_success) \times \text{UCB}(mean\_gain) \times \text{plateau\_factor}}{\text{gap\_complexity}}$$

- **UCB**: $\bar{x} + \sqrt{\frac{2 \ln N}{n}}$
- **Plateau factor**: 正常=1.0，冻结后=`FROZEN_PENALTY`(0.05)
- **Gap complexity** (P4): ≤5 行 → 0.7, ≤15 行 → 1.0, ≤30 行 → 1.2, >30 行 → 1.5

#### 奖励公式

$$R = 0.7 \cdot \Delta_{\text{line}} + 0.3 \cdot \Delta_{\text{branch}} + \text{status\_bonus} + \text{flaky\_penalty} - 0.05 \cdot \text{cost\_sec}$$

#### 关键常量

| 常量 | 值 | 说明 |
|------|---|------|
| `PLATEAU_THRESHOLD` | 3 | 连续 U 次数触发冻结 |
| `FROZEN_PENALTY` | 0.05 | 冻结臂的分数乘数 |
| `MAX_PULLS_PER_ARM` | 8 | 单臂最大尝试次数 |

#### 接口

| 方法 | 调用时机 | 说明 |
|------|---------|------|
| `add_arm(seg_id, missing_lines, missing_branches)` | 初始化时注册所有段 | 计算 `gap_complexity` |
| `select_batch(k)` | 每波开始 | 返回 top-k 段 ID |
| `update(seg_id, ir)` | 每次尝试完成 | 更新统计，检测 plateau |
| `mark_completed(seg_id)` | 段成功 | 从活跃集合移除 |
| `has_active_arms()` | 循环条件 | 是否还有未完成/未冻结的臂 |

#### 批次调度模式

主循环从"一次性调度所有段"变为"批次波次"模式：

```
while planner.has_active_arms():
    batch = planner.select_batch(k=concurrency)
    results = parallel_execute(batch)
    for result in results:
        planner.update(...)
    # 下一波重新评分，选择新 top-k
```

---

### 3.3 RepairOrchestrator — 两阶段修复器（P3）

**文件**: `src/coverup/agents/repair.py` (380 行)

#### 核心思想

编译/运行失败时，**先尝试确定性工具修复**（零 LLM 开销），只在工具修复不充分时才回退到 LLM。

#### 两阶段流程

```
编译/运行失败
    │
    ▼
Phase 1: RepairOrchestrator.try_tool_repair()
    │  遍历 (language, error_category) 注册的修复函数
    │  + 通配符修复函数（如 cargo check autofix）
    │
    ├─ 修复成功 → 重新编译验证 → 跳过 LLM（节省一次调用）
    │
    └─ 修复不充分 → Phase 2
         │
         ▼
Phase 2: LLM 回退
    │  memory.format_entry_for_error(ir) → 获取针对性建议
    │  附加到 error_prompt → LLM 修正
```

#### 已注册的修复函数

| 语言 | 类别 | 函数 | 能力 |
|------|------|------|------|
| **Rust** | IMPORT | `_rust_fix_imports` | 调用 `_autofix_submodule_imports` + 正则匹配 "cannot find X" 插入 `use` 语句 |
| **Rust** | TYPE | `_rust_fix_type_hints` | 检测 `&str`/`String` 不匹配 |
| **Rust** | VISIBILITY | `_rust_fix_visibility` | 检测 "is private" 错误 |
| **Rust** | `*` (通配) | `_rust_cargo_check_autofix` | **P3 新增**：应用 `cargo check --message-format=json` 的 `MachineApplicable` 建议 |
| **Python** | IMPORT | `_python_fix_imports` | 常见模块映射表（pytest/mock/os/sys 等） |
| **Python** | SYNTAX | `_python_fix_syntax` | 修复未闭合括号 |
| **Go** | IMPORT | `_go_fix_imports` | 移除未使用 import + 添加标准库 import |

#### Rust 结构化诊断（P3 关键增强）

`rust_backend.py` 新增两个函数：

- **`parse_cargo_check_json(output)`**: 解析 `cargo check --message-format=json` 的 JSONL 输出，提取诊断的 `code`, `level`, `message`, `spans`, `suggestions`
- **`apply_machine_applicable_fixes(code, diagnostics)`**: 只应用 `applicability == "MachineApplicable"` 的建议，按行号降序应用以保持偏移有效

---

### 3.4 TraceLogger — 结构化追踪日志（P0）

**文件**: `src/coverup/agents/trace.py` (100 行)

#### 核心思想

每次尝试写入一行 JSONL，包含完整的诊断信息，供离线分析和调参。

#### 字段

`ts`, `seg_id`, `attempt`, `action`, `outcome`, `phase`, `status`, `ir_category`, `ir_code`, `delta_line`, `delta_branch`, `cost_sec`, `cost_tokens_in`, `cost_tokens_out`, `tool_fixes`, `memory_injected`

#### 状态

**已实现并接入主循环**。通过 CLI 参数 `--trace-log PATH` 启用：

```bash
python -m coverup ... --trace-log /tmp/run-trace.jsonl
```

集成位置：`coverup.py` L510-517 初始化实例，L520-843 每次尝试自动记录。

---

### 3.5 CoverageBlocker — 覆盖率阻断解释（P5）

**文件**: `src/coverup/agents/blocker.py` (727 行)

#### 核心思想

自动分析源代码中**为什么某些行无法被覆盖**，将守卫条件（guard conditions）和变量来源（variable origins）提取出来，注入 prompt 帮助 LLM 生成能穿透阻断的测试。

#### 支持的语言

| 语言 | 解析方式 | 提取内容 |
|------|---------|---------|
| **Rust** | tree-sitter | if/match guard 条件 + 变量 let 绑定 + cfg 属性 |
| **Go** | tree-sitter | if/switch guard + 变量声明 + error check |
| **Python** | stdlib ast | if/elif guard + 变量赋值 + exception handler |

#### 输出格式

```python
@dataclass
class BlockerExplanation:
    guards: List[GuardCondition]    # 守卫条件列表
    origins: List[VariableOrigin]   # 变量来源列表
    summary: str                    # 人类可读摘要
```

#### 接口

| 方法 | 说明 |
|------|------|
| `explain_blockers(source, missing_lines, language)` | 主入口，分析源码中未覆盖行的阻断原因 |
| `format_for_prompt(explanation)` | 将 BlockerExplanation 格式化为 LLM prompt 片段 |

#### 已知 TODO

- L282: "track implicit else blockers" — 追踪隐式 else 分支的阻断

---

## 4. DiagnosticIR — 统一诊断中间表示

**文件**: `src/coverup/diagnostic_ir.py`

所有语言的编译/运行错误统一转换为 `DiagnosticIR` 结构体，作为四个智能体组件的通信协议：

```python
@dataclass
class DiagnosticIR:
    phase: str              # "compile" | "runtime" | "timeout"
    status: str             # "fail" | "ok" | "timeout"
    error_category: str     # ErrorCategory enum 值
    error_code: str         # 语言特定错误码 (E0432, NameError, ...)
    message: str            # 原始错误消息
    delta_line: float       # 行覆盖增量
    delta_branch: float     # 分支覆盖增量
    cost_sec: float         # 耗时
    cost_tokens_in: int     # 输入 token 数
    cost_tokens_out: int    # 输出 token 数
```

`ErrorCategory` 枚举: `IMPORT`, `TYPE`, `VISIBILITY`, `OWNERSHIP`, `ASSERTION`, `PANIC`, `SYNTAX`, `TIMEOUT`, `UNKNOWN`

---

## 5. 数据流全景

```
                     ┌──────────────┐
                     │  UCBPlanner  │
                     │ select_batch │
                     └──────┬───────┘
                            │ top-k segment IDs
                            ▼
                ┌───────────────────────┐
                │   初始 prompt 构建      │
                │ ├─ 代码段上下文          │
                │ ├─ 缺失行/分支标注       │
                │ └─ Memory 处方注入 ◄────┤ ReflectiveMemory.format_for_prompt()
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │     LLM 生成测试       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  backend 编译 & 运行    │
                │  (cargo test / pytest  │
                │   / go test)           │
                └───────────┬───────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         ┌──────────┐           ┌──────────┐
         │  成功 (G)  │           │  失败 (F)  │
         └─────┬────┘           └─────┬────┘
               │                      │
               │    ┌─────────────────┤
               │    │                 │
               │    ▼                 ▼
               │  classify_error() → DiagnosticIR
               │    │
               │    ├─→ RepairOrchestrator.try_tool_repair()
               │    │     ├─ 修复成功 → 重新验证（跳过 LLM）
               │    │     └─ 修复失败 → Memory hint → LLM error_prompt
               │    │
               │    └─→ memory.record(ir, action, succeeded=False)
               │         planner.update(seg_id, ir)
               │
               ├─→ memory.record(ir, action, succeeded=True)
               │    planner.update(seg_id, ir)
               │    planner.mark_completed(seg_id)
               │
               ▼
         下一波 select_batch()
```

---

## 6. CLI 控制标志

| 标志 | 控制的组件 | 用途 |
|------|-----------|------|
| `--no-agent-memory` | ReflectiveMemory | 消融实验：禁用食谱库 |
| `--no-agent-repair` | RepairOrchestrator | 消融实验：禁用工具修复 |
| `--no-agent-planner` | UCBPlanner | 消融实验：禁用调度器，恢复一次性全量调度 |
| （三者同时启用）| 全部禁用 | 等价于原版 CoverUp baseline |

标志定义位于 `coverup.py` 的 `parse_args()` 中（约 L198-207）。

---

## 7. 跨语言实验结果 (v3)

### 7.1 综合结果

| 项目 | 语言 | Baseline | Agent | Agent Δ | 失败减少 |
|------|------|----------|-------|---------|---------|
| **Flask** | Python | 94.9% | **95.8%** | **+0.9pp** ✅ | -14.4% |
| **similar** | Rust | 90.9% | **92.5%** | **+1.6pp** ✅ | -36.4% |
| fastrand | Rust | **97.5%** | 96.2% | -1.3pp ❌ | -41.2% |
| cobra | Go | **97.3%** | 96.9% | -0.4pp ❌ | -10.1% |

### 7.2 与发表论文对比

| 对比 | 论文结果 | 我们的结果 |
|------|---------|-----------|
| Flask: CoverUp + GPT-4o | 94.4% | Agent + DeepSeek = **95.8%** (+1.4pp) |
| fastrand: PALM + GPT-4o-mini | 93.94% (独立) | Baseline + DeepSeek = **97.5%** (增量) |

**核心叙事**: "弱 LLM (DeepSeek Coder, ~30 倍便宜) + 智能 Agent ≥ 强 LLM (GPT-4o) + 朴素方法"

### 7.3 关键发现

1. **Agent 在大/复杂项目上收益显著** — Memory 积累经验 + Planner 精准分配预算
2. **Agent 在小/简单项目上可能有害** — 学习开销 > 收益，需自适应调节
3. **Agent 一致地减少失败率** — 所有 4 个项目上 F 都下降 10-41%
4. **Agent 倾向更少 pass** — 有时过早终止，需 min_passes 机制

---

## 8. 已知局限与下一步改进

### 8.1 待修复的核心问题

| 问题 | 方案 | 工作量 |
|------|------|--------|
| Agent 在小项目上过早终止 | 引入 `min_passes` + 解冻有潜力的 arms | 0.5 天 |
| Agent 探索强度不随项目规模调整 | 根据 `num_segments` 自动调节 `exploration_factor` | 0.5 天 |
| U 测试缺乏差异分析 | 在重试时注入"实际覆盖 vs 目标覆盖"的差分信息 | 1 天 |

### 8.2 增强方向

| 方向 | 描述 | 预期收益 |
|------|------|---------|
| 跨段模式学习 | 提取项目级通用模式（如"所有函数需 `use crate::X`"） | 减少重复错误 |
| 自适应温度 | 难段 (consecutive_useless ≥ 2) 提高 temperature | 突破 coverage plateau |
| 动态 Blocker | 利用运行时覆盖差分增强阻断分析 | 提升 P5 准确性 |
| 测试精炼 | 贪心最小覆盖子集选择 | 减少冗余测试 30-50% |

---

## 9. 文件索引

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/coverup/agents/__init__.py` | 19 | 模块导出 |
| `src/coverup/agents/memory.py` | 468 | ReflectiveMemory + SuccessLevel 分层 |
| `src/coverup/agents/planner.py` | 336 | UCBPlanner 多臂赌博机 |
| `src/coverup/agents/repair.py` | 379 | RepairOrchestrator 两阶段修复 |
| `src/coverup/agents/blocker.py` | 727 | CoverageBlocker 覆盖率阻断解释 |
| `src/coverup/agents/trace.py` | 99 | TraceLogger JSONL 追踪 |
| `src/coverup/diagnostic_ir.py` | 278 | DiagnosticIR 统一表示 |
| `src/coverup/coverup.py` | 1098 | 主循环 (Agent 集成 + Wave 调度) |
| `src/coverup/languages/rust_backend.py` | ~2000 | Rust 后端 (含 cargo check JSON) |
